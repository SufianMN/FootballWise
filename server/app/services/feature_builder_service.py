import os

import pandas as pd

from app.core.logger import get_logger

logger = get_logger(__name__)


class FeatureBuilderService:
    def __init__(self):
        self.dataset_df = None

    def load_data(self):
        logger.info("Loading Feature Builder data...")
        from pathlib import Path

        default_base_dir = Path(__file__).resolve().parent.parent.parent.parent / "ml"
        data_dir = os.environ.get("DATA_DIRECTORY", str(default_base_dir / "data"))
        dataset_path = os.path.join(data_dir, "features", "match_dataset.csv")

        try:
            if os.path.exists(dataset_path):
                self.dataset_df = pd.read_csv(dataset_path)
            else:
                logger.warning(f"Dataset file not found at {dataset_path}")
        except Exception as e:
            logger.error(f"Error loading dataset_df in feature_builder_service: {e}", exc_info=True)

    def build_latest_team_features(self, team_id, prefix, feature_columns):
        if self.dataset_df is None:
            return {}

        tid = float(team_id)
        team_home = self.dataset_df[self.dataset_df["home_team_id"] == tid]
        team_away = self.dataset_df[self.dataset_df["away_team_id"] == tid]

        latest_home = (
            team_home.sort_values(by="match_date", ascending=False).iloc[0]
            if len(team_home) > 0
            else None
        )
        latest_away = (
            team_away.sort_values(by="match_date", ascending=False).iloc[0]
            if len(team_away) > 0
            else None
        )

        latest_row = None
        was_home = True

        if latest_home is not None and latest_away is not None:
            if latest_home["match_date"] >= latest_away["match_date"]:
                latest_row = latest_home
                was_home = True
            else:
                latest_row = latest_away
                was_home = False
        elif latest_home is not None:
            latest_row = latest_home
            was_home = True
        elif latest_away is not None:
            latest_row = latest_away
            was_home = False
        else:
            return None

        source_prefix = "home_" if was_home else "away_"

        features = {}
        for col in feature_columns:
            if col.startswith(prefix + "_"):
                suffix = col[len(prefix + "_") :]
                source_col = f"{source_prefix}{suffix}"

                if source_col in latest_row:
                    features[col] = latest_row[source_col]
                else:
                    features[col] = 0.0

        return features

    def build_h2h_features(self, home_team_id, away_team_id, feature_columns):
        if self.dataset_df is None:
            return {}

        tid1, tid2 = float(home_team_id), float(away_team_id)

        h2h_matches = self.dataset_df[
            (
                (self.dataset_df["home_team_id"] == tid1)
                & (self.dataset_df["away_team_id"] == tid2)
            )
            | (
                (self.dataset_df["home_team_id"] == tid2)
                & (self.dataset_df["away_team_id"] == tid1)
            )
        ]

        if len(h2h_matches) > 0:
            latest = h2h_matches.sort_values(by="match_date", ascending=False).iloc[0]
            features = {}

            is_same_orientation = latest["home_team_id"] == tid1

            for col in feature_columns:
                if col.startswith("h2h_"):
                    if col == "h2h_home_wins":
                        features[col] = (
                            latest["h2h_home_wins"]
                            if is_same_orientation
                            else latest["h2h_away_wins"]
                        )
                    elif col == "h2h_away_wins":
                        features[col] = (
                            latest["h2h_away_wins"]
                            if is_same_orientation
                            else latest["h2h_home_wins"]
                        )
                    else:
                        features[col] = latest[col] if col in latest else 0.0
            return features

        return {col: 0.0 for col in feature_columns if col.startswith("h2h_")}

    def build_match_features(self, home_team_id, away_team_id, feature_columns):
        """Constructs the complete ML feature vector for prediction."""
        home_features = self.build_latest_team_features(
            home_team_id, "home", feature_columns
        )
        away_features = self.build_latest_team_features(
            away_team_id, "away", feature_columns
        )
        h2h_features = self.build_h2h_features(
            home_team_id, away_team_id, feature_columns
        )

        if home_features is None or away_features is None:
            return None, None, None, None

        combined = {**home_features, **away_features, **h2h_features}

        vector = []
        for col in feature_columns:
            vector.append(combined.get(col, 0.0))

        X = pd.DataFrame([vector], columns=feature_columns)

        return X, home_features, away_features, h2h_features


feature_builder_service = FeatureBuilderService()
