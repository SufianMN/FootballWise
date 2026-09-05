from functools import lru_cache
from typing import Any, Dict, Optional
from langchain_core.tools import tool

from app.core.logger import get_logger
from app.services.player_service import player_service
from app.services.prediction_service import prediction_service
from app.services.team_service import team_service
from app.utils.helpers import convert_numpy_types
from .rag import search_match_history_context

logger = get_logger(__name__)


@lru_cache(maxsize=128)
def resolve_team_id(name_or_id: str) -> Optional[str]:
    """Resolve a team name or ID string to the exact team ID string used in team_service."""
    if not team_service.team_names:
        team_service.load_data()

    clean = str(name_or_id).strip()
    if clean in team_service.team_names:
        return clean

    query = clean.lower()
    for tid, tname in team_service.team_names.items():
        if tname.lower() == query:
            return tid

    for tid, tname in team_service.team_names.items():
        if query in tname.lower() or tname.lower() in query:
            return tid

    return None


@lru_cache(maxsize=256)
def resolve_player_id(name_or_id: str) -> Optional[int]:
    """Resolve a player name or ID to the exact player_id integer used in player_service."""
    if player_service.players_df.empty:
        player_service.load_data()

    if player_service.players_df.empty:
        return None

    clean = str(name_or_id).strip()
    try:
        pid = int(clean)
        if not player_service.players_df[player_service.players_df["player_id"] == pid].empty:
            return pid
    except ValueError:
        pass

    query = clean.lower()
    matches = player_service.players_df[
        player_service.players_df["player_name"].str.lower().str.contains(query, regex=False, na=False)
    ]
    if not matches.empty:
        return int(matches.iloc[0]["player_id"])

    return None


@tool
def predict_match(home_team: str, away_team: str) -> Dict[str, Any]:
    """
    Predict the outcome of a football match using FootballWise's existing XGBoost model.
    Accepts team names or IDs. Returns compact win/draw/loss probabilities and confidence levels.
    """
    h_id = resolve_team_id(home_team)
    a_id = resolve_team_id(away_team)

    if not h_id or not a_id:
        return {
            "error": f"Could not find matching teams in database for '{home_team}' or '{away_team}'."
        }

    if h_id == a_id:
        return {"error": "Home team and Away team must be different."}

    try:
        pred = prediction_service.predict(h_id, a_id)
        h_name = team_service.team_names.get(h_id, home_team)
        a_name = team_service.team_names.get(a_id, away_team)

        # Compact response to conserve Groq Free Plan tokens
        return convert_numpy_types({
            "home_team": h_name,
            "away_team": a_name,
            "predicted_result": pred.get("predicted_result"),
            "confidence": pred.get("confidence"),
            "confidence_level": pred.get("confidence_level"),
            "home_win_probability": pred.get("home_win_probability"),
            "draw_probability": pred.get("draw_probability"),
            "away_win_probability": pred.get("away_win_probability"),
            "top_drivers": pred.get("top_features", [])[:3] if isinstance(pred.get("top_features"), list) else [],
        })
    except Exception as e:
        logger.error(f"Error in predict_match tool: {e}", exc_info=True)
        return {"error": f"Match prediction error: {str(e)}"}


@tool
def explain_match_prediction(home_team: str, away_team: str) -> Dict[str, Any]:
    """
    Explain the FootballWise XGBoost match prediction using calculated SHAP feature impacts.
    Accepts team names or IDs and returns the top 5 statistical features driving the prediction.
    """
    h_id = resolve_team_id(home_team)
    a_id = resolve_team_id(away_team)

    if not h_id or not a_id:
        return {
            "error": f"Could not find matching teams for '{home_team}' or '{away_team}'."
        }

    try:
        pred = prediction_service.predict(h_id, a_id)
        h_name = team_service.team_names.get(h_id, home_team)
        a_name = team_service.team_names.get(a_id, away_team)

        raw_features = pred.get("top_features", [])
        # Cap to top 5 SHAP features maximum to stay strictly within token limits
        compact_features = raw_features[:5] if isinstance(raw_features, list) else raw_features
        raw_insights = pred.get("insights", [])
        compact_insights = raw_insights[:3] if isinstance(raw_insights, list) else raw_insights

        return convert_numpy_types({
            "home_team": h_name,
            "away_team": a_name,
            "predicted_result": pred.get("predicted_result"),
            "top_shap_features": compact_features,
            "tactical_insights": compact_insights,
        })
    except Exception as e:
        logger.error(f"Error in explain_match_prediction tool: {e}", exc_info=True)
        return {"error": f"SHAP explanation error: {str(e)}"}


@tool
def get_team_stats(team_name: str) -> Dict[str, Any]:
    """
    Retrieve exact numerical team statistics (goals, xG, possession, win rate, clean sheets)
    from FootballWise's team dataset layer. Returns compact statistics.
    """
    tid = resolve_team_id(team_name)
    if not tid:
        return {"error": f"Team '{team_name}' not found in database."}

    stats = team_service.get_team_stats(tid)
    if not stats:
        return {"error": f"No statistical data found for team '{team_name}'."}

    if isinstance(stats, dict):
        keys = ["team_name", "matches_played", "win_rate", "goals_scored", "goals_conceded", "avg_xg", "avg_xg_conceded", "clean_sheets", "possession_avg", "form"]
        compact = {k: stats[k] for k in keys if k in stats}
        return convert_numpy_types(compact if compact else stats)

    return convert_numpy_types(stats)


@tool
def get_player_stats(player_name: str) -> Dict[str, Any]:
    """
    Retrieve exact numerical statistics for a specific football player (goals, xG, passes, tackles, assists)
    from FootballWise's player dataset layer. Returns compact statistics.
    """
    pid = resolve_player_id(player_name)
    if not pid:
        return {"error": f"Player '{player_name}' not found in database."}

    details = player_service.get_player_details(pid)
    if not details:
        return {"error": f"No details found for player '{player_name}'."}

    if isinstance(details, dict):
        keys = ["player_name", "team_name", "position", "matches", "goals", "assists", "xg", "pass_accuracy", "tackles"]
        compact = {k: details[k] for k in keys if k in details}
        return convert_numpy_types(compact if compact else details)

    return convert_numpy_types(details)


@tool
def compare_players_tool(player1_name: str, player2_name: str) -> Dict[str, Any]:
    """
    Compare numerical statistics of two football players side-by-side.
    """
    p1_id = resolve_player_id(player1_name)
    p2_id = resolve_player_id(player2_name)

    if not p1_id or not p2_id:
        return {
            "error": f"Could not locate one or both players: '{player1_name}', '{player2_name}'."
        }

    comparison = player_service.compare_players(p1_id, p2_id)
    return convert_numpy_types(comparison)


@tool
def search_match_history(query: str) -> str:
    """
    Search historical football match information, key timeline events, goals, cards, and event narratives
    using the FootballWise RAG knowledge base.
    """
    return search_match_history_context(query)
