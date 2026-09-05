import ast
import json
import os
from pathlib import Path
import pandas as pd

from app.core.logger import get_logger

logger = get_logger(__name__)


def parse_match_events(json_path: str, match_meta: dict) -> list:
    """Parse a StatsBomb event JSON file into structured textual documents with metadata."""
    if not os.path.exists(json_path):
        return []

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            events = json.load(f)
    except Exception as e:
        logger.error(f"Failed to read JSON event file {json_path}: {e}")
        return []

    match_id = str(match_meta.get("match_id", ""))
    home_team = str(match_meta.get("home_team", "Home Team"))
    away_team = str(match_meta.get("away_team", "Away Team"))
    date = str(match_meta.get("date", "Unknown"))
    comp = str(match_meta.get("competition", "Unknown"))
    season = str(match_meta.get("season", "Unknown"))
    home_score = match_meta.get("home_score", 0)
    away_score = match_meta.get("away_score", 0)

    goals = []
    high_xg_shots = []
    cards = []
    team_shots = {home_team: 0, away_team: 0}
    team_xg = {home_team: 0.0, away_team: 0.0}

    for ev in events:
        ev_type = ev.get("type", {}).get("name", "")
        minute = ev.get("minute", 0)
        team_name = ev.get("team", {}).get("name", "")
        player_name = ev.get("player", {}).get("name", "Unknown Player")

        # 1. Shots & Goals
        if ev_type == "Shot":
            shot = ev.get("shot", {})
            xg = shot.get("statsbomb_xg", 0.0)
            outcome = shot.get("outcome", {}).get("name", "")

            if team_name in team_shots:
                team_shots[team_name] += 1
                team_xg[team_name] += xg
            else:
                team_shots[team_name] = 1
                team_xg[team_name] = xg

            if outcome == "Goal":
                goals.append(f"- {minute}': Goal by {player_name} ({team_name}) [xG: {xg:.2f}]")
            elif xg >= 0.15:
                high_xg_shots.append(
                    f"- {minute}': Dangerous chance for {player_name} ({team_name}) - Shot outcome: {outcome} [xG: {xg:.2f}]"
                )

        # 2. Cards & Discipline
        foul = ev.get("foul_committed", {})
        bad_behaviour = ev.get("bad_behaviour", {})
        card_info = foul.get("card", {}) or bad_behaviour.get("card", {})
        if card_info and "name" in card_info:
            card_type = card_info["name"]
            cards.append(f"- {minute}': {card_type} for {player_name} ({team_name})")

    # Format text description
    goals_text = "\n".join(goals) if goals else "- No goals recorded in event log."
    chances_text = "\n".join(high_xg_shots[:8]) if high_xg_shots else "- No major high-xG chances."
    cards_text = "\n".join(cards[:8]) if cards else "- Clean match with no cards."

    home_xg_val = team_xg.get(home_team, 0.0)
    away_xg_val = team_xg.get(away_team, 0.0)
    home_shot_count = team_shots.get(home_team, 0)
    away_shot_count = team_shots.get(away_team, 0)

    content = f"""Match Event Report: {home_team} vs {away_team}
Competition: {comp} ({season}) | Date: {date}
Final Score: {home_team} {home_score} - {away_score} {away_team}
Total Expected Goals (xG): {home_team} ({home_xg_val:.2f} xG from {home_shot_count} shots) vs {away_team} ({away_xg_val:.2f} xG from {away_shot_count} shots)

Goals Timeline:
{goals_text}

Key Attacking Chances:
{chances_text}

Discipline & Cards:
{cards_text}
"""

    metadata = {
        "match_id": match_id,
        "home_team": home_team,
        "away_team": away_team,
        "date": date,
        "competition": comp,
        "season": season,
        "document_type": "match_events",
    }

    return [{"content": content, "metadata": metadata}]


def get_chroma_db_dir() -> Path:
    """Get persistent ChromaDB storage location."""
    base_dir = Path(__file__).resolve().parent.parent.parent
    return base_dir / "data" / "chroma_db"


def build_rag_index():
    """Build or rebuild the ChromaDB index for FootballWise RAG offline."""
    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    data_dir = Path(os.environ.get("DATA_DIRECTORY", str(base_dir / "ml" / "data")))
    processed_dir = data_dir / "processed"
    raw_dir = data_dir / "raw"
    matches_csv = processed_dir / "processed_matches.csv"

    if not matches_csv.exists():
        logger.error(f"Cannot build RAG index: {matches_csv} does not exist.")
        return

    logger.info("Reading matches dataset...")
    df_matches = pd.read_csv(matches_csv)

    max_matches = int(os.environ.get("RAG_MAX_MATCHES", "50"))
    all_docs = []
    processed_count = 0
    for idx, row in df_matches.iterrows():
        if processed_count >= max_matches:
            break

        match_id = str(row["match_id"])
        json_path = raw_dir / f"events_{match_id}.json"
        if not json_path.exists():
            continue


        comp_raw = str(row.get("competition", ""))
        season_raw = str(row.get("season", ""))

        comp_name = "Unknown"
        season_name = "Unknown"

        try:
            if comp_raw and comp_raw != "nan":
                c_dict = ast.literal_eval(comp_raw)
                comp_name = c_dict.get("competition_name", "Unknown")
        except Exception:
            pass

        try:
            if season_raw and season_raw != "nan":
                s_dict = ast.literal_eval(season_raw)
                season_name = s_dict.get("season_name", "Unknown")
        except Exception:
            pass

        match_meta = {
            "match_id": match_id,
            "home_team": str(row.get("home_team_name", row.get("home_team", ""))),
            "away_team": str(row.get("away_team_name", row.get("away_team", ""))),
            "date": str(row.get("match_date", "")),
            "competition": comp_name,
            "season": season_name,
            "home_score": row.get("home_score", 0),
            "away_score": row.get("away_score", 0),
        }

        docs = parse_match_events(str(json_path), match_meta)
        all_docs.extend(docs)
        processed_count += 1

        if processed_count % 100 == 0:
            logger.info(f"Parsed {processed_count} match event JSONs...")

    logger.info(f"Successfully generated {len(all_docs)} match narrative documents from {processed_count} StatsBomb event JSON files.")

    if not all_docs:
        logger.warning("No documents created for RAG index.")
        return

    chroma_dir = get_chroma_db_dir()
    if chroma_dir.exists():
        import shutil
        try:
            shutil.rmtree(chroma_dir)
        except Exception as e:
            logger.warning(f"Could not clear existing chroma_dir: {e}")

    chroma_dir.mkdir(parents=True, exist_ok=True)


    try:
        from langchain_community.vectorstores import Chroma
        from langchain_core.documents import Document
        from langchain_openai import OpenAIEmbeddings

        api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("LLM_API_KEY")
        if api_key:
            embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=api_key)
            logger.info("Using OpenAIEmbeddings (text-embedding-3-small).")
        else:
            try:
                from langchain_community.embeddings import HuggingFaceEmbeddings
                embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
                logger.info("Using HuggingFaceEmbeddings (all-MiniLM-L6-v2) for local embedding generation.")
            except Exception:
                from langchain_community.embeddings import FakeEmbeddings
                embeddings = FakeEmbeddings(size=384)
                logger.warning("Falling back to FakeEmbeddings.")

        lc_docs = [Document(page_content=d["content"], metadata=d["metadata"]) for d in all_docs]

        db = Chroma.from_documents(
            documents=lc_docs,
            embedding=embeddings,
            persist_directory=str(chroma_dir),
            collection_name="footballwise_events",
        )
        logger.info(f"Successfully built ChromaDB index with {len(lc_docs)} documents at {chroma_dir}")
        print(f"RAG Index Build Complete: {len(lc_docs)} documents indexed across {processed_count} match JSON files.")
    except Exception as e:
        logger.error(f"Error building ChromaDB vector index: {e}", exc_info=True)


if __name__ == "__main__":
    build_rag_index()
