import pandas as pd

from app.core.logger import get_logger

logger = get_logger(__name__)


class PlayerService:
    def __init__(self):
        self.players_df = pd.DataFrame()

    def load_data(self):
        """Load player statistics from the processed CSV file."""
        import os
        from pathlib import Path

        default_base_dir = Path(__file__).resolve().parent.parent.parent.parent / "ml"
        data_dir = os.environ.get("DATA_DIRECTORY", str(default_base_dir / "data"))
        csv_path = os.path.join(data_dir, "processed", "player_stats.csv")

        if not os.path.exists(csv_path):
            logger.warning(
                f"Player statistics dataset not found at {csv_path}. "
                "The server will start, but Player Analytics will be empty."
            )
            self.players_df = pd.DataFrame()
            return

        try:
            self.players_df = pd.read_csv(csv_path)
            self.players_df.fillna(0, inplace=True)
            logger.info(f"Loaded {len(self.players_df)} player season records.")
        except Exception as e:
            logger.error(f"Error loading player stats: {e}")
            self.players_df = pd.DataFrame()

    def get_players(self):
        """Return a lightweight list of players for search selectors."""
        if self.players_df.empty:
            return []

        # Deduplicate players (they might have multiple seasons)
        # We will keep the most recent team and competition they played in.
        # For simplicity, we just drop duplicates based on player_id, keeping the first occurrence.
        # Sorting by season descending would be better, assuming season format is string or int.
        try:
            sorted_df = self.players_df.sort_values(by="season", ascending=False)
            unique_players = sorted_df.drop_duplicates(
                subset=["player_id"], keep="first"
            )

            result = unique_players[
                ["player_id", "player_name", "team_name", "position"]
            ].to_dict("records")

            # Map keys to match frontend expectations
            mapped = []
            for row in result:
                mapped.append(
                    {
                        "id": str(row["player_id"]),
                        "name": row["player_name"],
                        "team": row["team_name"],
                        "position": row["position"],
                    }
                )
            return mapped
        except Exception as e:
            logger.error(f"Error getting players: {e}")
            return []

    def get_player_details(self, player_id: int):
        """Return comprehensive season-level stats, advanced metrics, and pre-computed radar percentiles."""
        if self.players_df.empty:
            return None

        player_data = self.players_df[self.players_df["player_id"] == player_id]
        if player_data.empty:
            return None

        # If a player has multiple seasons, we can either aggregate or return the latest.
        # Let's aggregate their stats across all available seasons for the 'overall' profile,
        # and also provide the latest team/competition info.
        latest = player_data.sort_values(by="season", ascending=False).iloc[0]

        # Aggregated stats
        matches = int(player_data["matches"].sum())
        goals = int(player_data["goals"].sum())
        xg = float(player_data["xg"].sum())
        assists = int(player_data["assists"].sum())
        shots = int(player_data["shots"].sum())
        shots_on_target = int(player_data["shots_on_target"].sum())
        key_passes = int(player_data["key_passes"].sum())
        passes = int(player_data["passes"].sum())
        completed_passes = int(player_data["completed_passes"].sum())
        dribbles = int(player_data["dribbles"].sum())
        successful_dribbles = int(player_data["successful_dribbles"].sum())
        tackles = int(player_data["tackles"].sum())
        interceptions = int(player_data["interceptions"].sum())
        clearances = int(player_data["clearances"].sum())
        yellow_cards = int(player_data["yellow_cards"].sum())
        red_cards = int(player_data["red_cards"].sum())
        fouls = int(player_data["fouls"].sum())

        # Advanced/Calculated metrics
        pass_accuracy = (completed_passes / passes * 100) if passes > 0 else 0
        dribble_success = (successful_dribbles / dribbles * 100) if dribbles > 0 else 0
        goals_per_match = (goals / matches) if matches > 0 else 0
        xg_per_match = (xg / matches) if matches > 0 else 0
        shot_accuracy = (shots_on_target / shots * 100) if shots > 0 else 0
        shot_conversion = (goals / shots * 100) if shots > 0 else 0
        goal_contribution = goals + assists

        # Normalization for Radar Chart
        # We compare this player's per-match stats to the whole dataset's per-match stats.
        # Calculate dataset percentiles
        all_matches = self.players_df.groupby("player_id")["matches"].sum()
        valid_players = all_matches[
            all_matches >= 5
        ].index  # Filter players with at least 5 matches

        filtered_df = self.players_df[self.players_df["player_id"].isin(valid_players)]
        agg_df = filtered_df.groupby("player_id").sum()

        agg_df["goals_pm"] = agg_df["goals"] / agg_df["matches"]
        agg_df["xg_pm"] = agg_df["xg"] / agg_df["matches"]
        agg_df["assists_pm"] = agg_df["assists"] / agg_df["matches"]
        agg_df["passes_pm"] = agg_df["passes"] / agg_df["matches"]
        agg_df["dribbles_pm"] = agg_df["successful_dribbles"] / agg_df["matches"]
        agg_df["defending_pm"] = (agg_df["tackles"] + agg_df["interceptions"]) / agg_df[
            "matches"
        ]
        agg_df["progression_pm"] = agg_df["key_passes"] / agg_df["matches"]

        def get_percentile(column, value):
            if agg_df.empty or matches == 0:
                return 50
            return int((agg_df[column] <= value).mean() * 100)

        radar = {
            "Goals": get_percentile("goals_pm", goals_per_match),
            "xG": get_percentile("xg_pm", xg_per_match),
            "Assists": get_percentile(
                "assists_pm", (assists / matches) if matches > 0 else 0
            ),
            "Passing": get_percentile(
                "passes_pm", (passes / matches) if matches > 0 else 0
            ),
            "Dribbling": get_percentile(
                "dribbles_pm", (successful_dribbles / matches) if matches > 0 else 0
            ),
            "Defending": get_percentile(
                "defending_pm",
                ((tackles + interceptions) / matches) if matches > 0 else 0,
            ),
            "Progression": get_percentile(
                "progression_pm", (key_passes / matches) if matches > 0 else 0
            ),
        }

        # Trend charts (season by season)
        trends = []
        for _, row in player_data.sort_values(by="season").iterrows():
            m = row["matches"]
            if m > 0:
                trends.append(
                    {
                        "season": row["season"],
                        "goals": int(row["goals"]),
                        "xg": float(row["xg"]),
                        "assists": int(row["assists"]),
                        "matches": int(row["matches"]),
                    }
                )

        return {
            "id": player_id,
            "name": latest["player_name"],
            "team": latest["team_name"],
            "position": latest["position"],
            "competition": latest["competition"],
            "season": latest["season"],
            "matches": matches,
            "attacking": {
                "goals": goals,
                "xg": xg,
                "shots": shots,
                "shots_on_target": shots_on_target,
                "shot_accuracy": shot_accuracy,
                "goals_per_match": goals_per_match,
                "xg_per_match": xg_per_match,
            },
            "creativity": {"assists": assists, "key_passes": key_passes},
            "passing": {
                "passes": passes,
                "completed_passes": completed_passes,
                "pass_accuracy": pass_accuracy,
            },
            "dribbling": {
                "dribbles": dribbles,
                "successful_dribbles": successful_dribbles,
                "dribble_success": dribble_success,
            },
            "defending": {
                "tackles": tackles,
                "interceptions": interceptions,
                "clearances": clearances,
            },
            "discipline": {
                "yellow_cards": yellow_cards,
                "red_cards": red_cards,
                "fouls": fouls,
            },
            "advanced": {
                "goals_minus_xg": goals - xg,
                "goal_contribution": goal_contribution,
                "shot_conversion": shot_conversion,
            },
            "radar": radar,
            "trends": trends,
        }

    def compare_players(self, player1_id: int, player2_id: int):
        p1 = self.get_player_details(player1_id)
        p2 = self.get_player_details(player2_id)
        return {"player1": p1, "player2": p2}


player_service = PlayerService()
