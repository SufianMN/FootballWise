import ast
import os

import pandas as pd

from app.core.logger import get_logger

from ..utils.helpers import convert_numpy_types

logger = get_logger(__name__)


class LeagueService:
    def __init__(self):
        self.df_logs = None
        self.competitions_map = {}

    def load_data(self):
        logger.info("Loading league analytics data...")
        from pathlib import Path

        default_base_dir = Path(__file__).resolve().parent.parent.parent.parent / "ml"
        data_dir = os.environ.get("DATA_DIRECTORY", str(default_base_dir / "data"))

        processed_dir = os.path.join(data_dir, "processed")

        matches_path = os.path.join(processed_dir, "processed_matches.csv")
        stats_path = os.path.join(processed_dir, "team_match_stats.csv")

        if not os.path.exists(matches_path) or not os.path.exists(stats_path):
            logger.warning(f"League data missing at {processed_dir}!")
            return

        try:
            df_matches = pd.read_csv(matches_path)
            df_stats = pd.read_csv(stats_path)
        except Exception as e:
            logger.error(f"Error loading league data: {e}", exc_info=True)
            return

        # Parse Competition and Season from string representations
        parsed_comps = []
        parsed_seasons = []
        for idx, row in df_matches.iterrows():
            comp_dict = (
                ast.literal_eval(row["competition"])
                if pd.notnull(row["competition"])
                else {}
            )
            season_dict = (
                ast.literal_eval(row["season"]) if pd.notnull(row["season"]) else {}
            )

            comp_id = str(comp_dict.get("competition_id", "unknown"))
            comp_name = comp_dict.get("competition_name", "Unknown Competition")
            season_id = str(season_dict.get("season_id", "unknown"))
            season_name = season_dict.get("season_name", "Unknown Season")

            parsed_comps.append((comp_id, comp_name))
            parsed_seasons.append((season_id, season_name))

        df_matches["parsed_comp_id"] = [c[0] for c in parsed_comps]
        df_matches["parsed_comp_name"] = [c[1] for c in parsed_comps]
        df_matches["parsed_season_id"] = [s[0] for s in parsed_seasons]
        df_matches["parsed_season_name"] = [s[1] for s in parsed_seasons]

        # Populate competitions map
        # We only keep the most recent season for each competition for simplicity, based on date
        df_matches["match_date"] = pd.to_datetime(df_matches["match_date"])
        df_matches = df_matches.sort_values("match_date")

        for name, group in df_matches.groupby("parsed_comp_id"):
            latest = group.iloc[-1]
            self.competitions_map[name] = {
                "id": name,
                "name": latest["parsed_comp_name"],
                "season_id": latest["parsed_season_id"],
                "season_name": latest["parsed_season_name"],
            }

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

        team_logs = []
        for _, row in df.iterrows():
            comp_id = row["parsed_comp_id"]
            season_id = row["parsed_season_id"]
            # We only want to add logs for the latest season of each competition
            if self.competitions_map.get(comp_id, {}).get("season_id") != season_id:
                continue

            h_score = row.get("home_score", 0)
            a_score = row.get("away_score", 0)

            home_passes = row.get("home_total_passes", 0)
            away_passes = row.get("away_total_passes", 0)
            home_passes = home_passes if pd.notnull(home_passes) else 0
            away_passes = away_passes if pd.notnull(away_passes) else 0
            total_passes = home_passes + away_passes

            home_poss = (home_passes / total_passes * 100) if total_passes > 0 else 50.0
            away_poss = (away_passes / total_passes * 100) if total_passes > 0 else 50.0

            # Home
            team_logs.append(
                {
                    "competition_id": comp_id,
                    "team_id": (
                        str(int(row["home_team_id"]))
                        if pd.notnull(row["home_team_id"])
                        else "unknown"
                    ),
                    "team_name": row.get("home_team_name", "Unknown"),
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
                    "points": (
                        3 if h_score > a_score else (1 if h_score == a_score else 0)
                    ),
                }
            )

            # Away
            team_logs.append(
                {
                    "competition_id": comp_id,
                    "team_id": (
                        str(int(row["away_team_id"]))
                        if pd.notnull(row["away_team_id"])
                        else "unknown"
                    ),
                    "team_name": row.get("away_team_name", "Unknown"),
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
                    "points": (
                        3 if a_score > h_score else (1 if a_score == h_score else 0)
                    ),
                }
            )

        self.df_logs = pd.DataFrame(team_logs)
        self.df_logs = self.df_logs.fillna(0)
        logger.info("League data successfully cached.")

    def get_competitions(self):
        if not self.competitions_map:
            return []
        res = []
        for k, v in self.competitions_map.items():
            if k != "unknown":
                res.append({"id": v["id"], "name": f"{v['name']} ({v['season_name']})"})
        return res

    def get_league_analytics(self, competition_id: str):
        if self.df_logs is None or competition_id not in self.competitions_map:
            return None

        comp_df = self.df_logs[self.df_logs["competition_id"] == competition_id]
        if len(comp_df) == 0:
            return None

        # Aggregate by team
        team_stats = []
        grouped = comp_df.groupby(["team_id", "team_name"])

        for (tid, tname), group in grouped:
            matches = len(group)
            if matches == 0:
                continue

            wins = group["win"].sum()
            draws = group["draw"].sum()
            losses = group["loss"].sum()
            gf = group["goals_scored"].sum()
            ga = group["goals_conceded"].sum()
            points = group["points"].sum()

            team_stats.append(
                {
                    "team_id": tid,
                    "team_name": tname,
                    "matches": int(matches),
                    "wins": int(wins),
                    "draws": int(draws),
                    "losses": int(losses),
                    "goals_for": int(gf),
                    "goals_against": int(ga),
                    "goal_difference": int(gf - ga),
                    "points": int(points),
                    "win_rate": round(float(wins / matches) * 100, 1),
                    "avg_goals": round(float(gf / matches), 2),
                    "avg_goals_conceded": round(float(ga / matches), 2),
                    "avg_xg": round(float(group["xg"].mean()), 2),
                    "avg_xga": round(float(group["xga"].mean()), 2),
                    "avg_possession": round(float(group["possession"].mean()), 1),
                    "avg_pass_accuracy": round(float(group["pass_accuracy"].mean()), 1),
                    "avg_shots": round(float(group["shots"].mean()), 1),
                    "avg_shots_on_target": round(
                        float(group["shots_on_target"].mean()), 1
                    ),
                    "avg_corners": round(float(group["corners"].mean()), 1),
                    "avg_yellow_cards": round(float(group["yellow_cards"].mean()), 1),
                    "avg_red_cards": round(float(group["red_cards"].mean()), 1),
                    "clean_sheet_pct": round(
                        float(group["clean_sheet"].mean()) * 100, 1
                    ),
                    "btts_pct": round(float(group["btts"].mean()) * 100, 1),
                }
            )

        if not team_stats:
            return None

        # Create DataFrame for easy sorting and ranking
        df_stats = pd.DataFrame(team_stats)

        # Sort for League Table (Points, then GD, then GF)
        df_table = df_stats.sort_values(
            ["points", "goal_difference", "goals_for"], ascending=[False, False, False]
        )
        df_table["position"] = range(1, len(df_table) + 1)

        table = df_table.to_dict("records")

        # Rankings (Top 5)
        rankings = {
            "top_attack": df_stats.nlargest(5, "goals_for")[
                ["team_name", "goals_for"]
            ].to_dict("records"),
            "top_defense": df_stats.nsmallest(5, "goals_against")[
                ["team_name", "goals_against"]
            ].to_dict("records"),
            "top_possession": df_stats.nlargest(5, "avg_possession")[
                ["team_name", "avg_possession"]
            ].to_dict("records"),
            "top_xg": df_stats.nlargest(5, "avg_xg")[["team_name", "avg_xg"]].to_dict(
                "records"
            ),
            "top_pass_accuracy": df_stats.nlargest(5, "avg_pass_accuracy")[
                ["team_name", "avg_pass_accuracy"]
            ].to_dict("records"),
        }

        leaders = {
            "best_attack_team": df_stats.loc[df_stats["goals_for"].idxmax()][
                "team_name"
            ],
            "best_attack_val": df_stats["goals_for"].max(),
            "best_defense_team": df_stats.loc[df_stats["goals_against"].idxmin()][
                "team_name"
            ],
            "best_defense_val": df_stats["goals_against"].min(),
            "highest_xg_team": df_stats.loc[df_stats["avg_xg"].idxmax()]["team_name"],
            "highest_xg_val": df_stats["avg_xg"].max(),
            "best_form_team": df_stats.loc[df_stats["win_rate"].idxmax()]["team_name"],
            "best_form_val": df_stats["win_rate"].max(),
            "best_pass_team": df_stats.loc[df_stats["avg_pass_accuracy"].idxmax()][
                "team_name"
            ],
            "best_pass_val": df_stats["avg_pass_accuracy"].max(),
        }

        # Basic Competition info
        comp_info = self.competitions_map[competition_id]

        result = {
            "competition": comp_info["name"],
            "season": comp_info["season_name"],
            "table": table,
            "rankings": rankings,
            "leaders": leaders,
        }

        return convert_numpy_types(result)


league_service = LeagueService()
