import os

import pandas as pd

from app.core.logger import get_logger

logger = get_logger(__name__)


class AnalyticsService:
    def __init__(self):
        self.df_logs = None
        self.team_names = {}

    def load_data(self):
        logger.info("Loading analytics data...")
        from pathlib import Path

        default_base_dir = Path(__file__).resolve().parent.parent.parent.parent / "ml"
        data_dir = os.environ.get("DATA_DIRECTORY", str(default_base_dir / "data"))

        processed_dir = os.path.join(data_dir, "processed")

        matches_path = os.path.join(processed_dir, "processed_matches.csv")
        stats_path = os.path.join(processed_dir, "team_match_stats.csv")

        if not os.path.exists(matches_path) or not os.path.exists(stats_path):
            logger.warning(f"Analytics data missing at {processed_dir}!")
            return

        try:
            df_matches = pd.read_csv(matches_path)
            df_stats = pd.read_csv(stats_path)
        except Exception as e:
            logger.error(f"Error loading analytics data: {e}", exc_info=True)
            return

        # Build Team Name mapping
        home_teams = df_matches[["home_team_id", "home_team_name"]].drop_duplicates()
        away_teams = df_matches[["away_team_id", "away_team_name"]].drop_duplicates()

        for _, row in home_teams.iterrows():
            if not pd.isna(row["home_team_id"]):
                self.team_names[str(int(row["home_team_id"]))] = row["home_team_name"]
        for _, row in away_teams.iterrows():
            if not pd.isna(row["away_team_id"]):
                self.team_names[str(int(row["away_team_id"]))] = row["away_team_name"]

        # Merge stats
        home_stats = df_stats.copy()
        home_stats = home_stats.rename(
            columns=lambda x: f"home_{x}" if x not in ["match_id", "team_id"] else x
        )
        home_stats = home_stats.rename(columns={"team_id": "home_team_id"})

        away_stats = df_stats.copy()
        away_stats = away_stats.rename(
            columns=lambda x: f"away_{x}" if x not in ["match_id", "team_id"] else x
        )
        away_stats = away_stats.rename(columns={"team_id": "away_team_id"})

        df = df_matches.merge(home_stats, on=["match_id", "home_team_id"], how="left")
        df = df.merge(away_stats, on=["match_id", "away_team_id"], how="left")

        df["match_date"] = pd.to_datetime(df["match_date"]).dt.strftime("%Y-%m-%d")
        df = df.sort_values("match_date")

        team_logs = []
        for _, row in df.iterrows():
            home_passes = row.get("home_total_passes", 0)
            away_passes = row.get("away_total_passes", 0)
            home_passes = home_passes if pd.notnull(home_passes) else 0
            away_passes = away_passes if pd.notnull(away_passes) else 0
            total_passes = home_passes + away_passes

            home_poss = (home_passes / total_passes * 100) if total_passes > 0 else 50.0
            away_poss = (away_passes / total_passes * 100) if total_passes > 0 else 50.0

            h_score = row.get("home_score", 0)
            a_score = row.get("away_score", 0)

            # Home
            team_logs.append(
                {
                    "match_date": row["match_date"],
                    "team_id": row["home_team_id"],
                    "is_home": True,
                    "goals_scored": h_score,
                    "goals_conceded": a_score,
                    "xg": row.get("home_xg", 0),
                    "xga": row.get("away_xg", 0),
                    "shots": row.get("home_shots", 0),
                    "shots_on_target": row.get("home_shots_on_target", 0),
                    "possession": home_poss,
                    "pass_accuracy": row.get("home_pass_accuracy", 0),
                    "corners": row.get("home_corners", 0),
                    "yellow_cards": row.get("home_yellow_cards", 0),
                    "red_cards": row.get("home_red_cards", 0),
                    "win": 1 if h_score > a_score else 0,
                    "draw": 1 if h_score == a_score else 0,
                    "loss": 1 if h_score < a_score else 0,
                    "clean_sheet": 1 if a_score == 0 else 0,
                    "btts": 1 if (h_score > 0 and a_score > 0) else 0,
                }
            )

            # Away
            team_logs.append(
                {
                    "match_date": row["match_date"],
                    "team_id": row["away_team_id"],
                    "is_home": False,
                    "goals_scored": a_score,
                    "goals_conceded": h_score,
                    "xg": row.get("away_xg", 0),
                    "xga": row.get("home_xg", 0),
                    "shots": row.get("away_shots", 0),
                    "shots_on_target": row.get("away_shots_on_target", 0),
                    "possession": away_poss,
                    "pass_accuracy": row.get("away_pass_accuracy", 0),
                    "corners": row.get("away_corners", 0),
                    "yellow_cards": row.get("away_yellow_cards", 0),
                    "red_cards": row.get("away_red_cards", 0),
                    "win": 1 if a_score > h_score else 0,
                    "draw": 1 if a_score == h_score else 0,
                    "loss": 1 if a_score < h_score else 0,
                    "clean_sheet": 1 if h_score == 0 else 0,
                    "btts": 1 if (h_score > 0 and a_score > 0) else 0,
                }
            )

        self.df_logs = pd.DataFrame(team_logs)
        self.df_logs = self.df_logs.fillna(0)
        logger.info("Analytics logs successfully cached.")

    def _aggregate(self, df):
        if len(df) == 0:
            return {}

        matches = len(df)
        wins = df["win"].sum()
        draws = df["draw"].sum()
        losses = df["loss"].sum()
        goals = df["goals_scored"].sum()
        conceded = df["goals_conceded"].sum()

        return {
            "matches": int(matches),
            "wins": int(wins),
            "draws": int(draws),
            "losses": int(losses),
            "goals_scored": int(goals),
            "goals_conceded": int(conceded),
            "goal_difference": int(goals - conceded),
            "clean_sheets": int(df["clean_sheet"].sum()),
            "win_rate": round(float(wins / matches), 2) if matches > 0 else 0,
            "avg_xg": round(float(df["xg"].mean()), 2),
            "avg_xga": round(float(df["xga"].mean()), 2),
            "avg_possession": round(float(df["possession"].mean()), 2),
            "avg_pass_accuracy": round(float(df["pass_accuracy"].mean()), 2),
            "avg_shots": round(float(df["shots"].mean()), 2),
            "avg_shots_on_target": round(float(df["shots_on_target"].mean()), 2),
            "avg_corners": round(float(df["corners"].mean()), 2),
            "avg_yellow_cards": round(float(df["yellow_cards"].mean()), 2),
            "avg_red_cards": round(float(df["red_cards"].mean()), 2),
            "btts_pct": round(float(df["btts"].mean()), 2),
        }

    def get_team_analytics(self, team_id: str):
        if self.df_logs is None:
            return None

        tid = float(team_id)
        team_df = self.df_logs[self.df_logs["team_id"] == tid].sort_values("match_date")

        if len(team_df) == 0:
            return None

        # Summary
        summary = self._aggregate(team_df)

        # Home / Away
        home_df = team_df[team_df["is_home"] == True]
        away_df = team_df[team_df["is_home"] == False]
        home_stats = self._aggregate(home_df)
        away_stats = self._aggregate(away_df)

        # Trends
        # We will return the raw match values chronologically, and a rolling average (e.g. over 5 matches)
        trends = {
            "form": [],
            "xg": [],
            "goals": [],
            "possession": [],
            "pass_accuracy": [],
            "shots": [],
        }

        rolling_window = 5
        rolling_win_rate = (
            team_df["win"].rolling(window=rolling_window, min_periods=1).mean()
        )
        rolling_xg = team_df["xg"].rolling(window=rolling_window, min_periods=1).mean()
        rolling_goals = (
            team_df["goals_scored"].rolling(window=rolling_window, min_periods=1).mean()
        )
        rolling_poss = (
            team_df["possession"].rolling(window=rolling_window, min_periods=1).mean()
        )
        rolling_pass = (
            team_df["pass_accuracy"]
            .rolling(window=rolling_window, min_periods=1)
            .mean()
        )
        rolling_shots = (
            team_df["shots"].rolling(window=rolling_window, min_periods=1).mean()
        )

        for i, row in enumerate(team_df.itertuples()):
            date = row.match_date
            trends["form"].append(
                {
                    "match_date": date,
                    "value": round(float(rolling_win_rate.iloc[i]) * 100, 1),
                }
            )
            trends["xg"].append(
                {"match_date": date, "value": round(float(rolling_xg.iloc[i]), 2)}
            )
            trends["goals"].append(
                {"match_date": date, "value": round(float(rolling_goals.iloc[i]), 2)}
            )
            trends["possession"].append(
                {"match_date": date, "value": round(float(rolling_poss.iloc[i]), 1)}
            )
            trends["pass_accuracy"].append(
                {"match_date": date, "value": round(float(rolling_pass.iloc[i]), 1)}
            )
            trends["shots"].append(
                {"match_date": date, "value": round(float(rolling_shots.iloc[i]), 1)}
            )

        return {
            "team": {"id": team_id, "name": self.team_names.get(team_id, "Unknown")},
            "summary": summary,
            "trends": trends,
            "home_away": {"home": home_stats, "away": away_stats},
        }


analytics_service = AnalyticsService()
