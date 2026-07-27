import shap

from app.core.logger import get_logger

logger = get_logger(__name__)


class ExplainabilityService:
    def __init__(self):
        self.explainer = None

    def initialize(self, model):
        # Initialize the SHAP TreeExplainer with the trained XGBoost model
        logger.info("Initializing SHAP TreeExplainer...")

        # Handle CalibratedClassifierCV wrappers
        base_model = model
        if hasattr(model, "calibrated_classifiers_"):
            base_model = model.calibrated_classifiers_[0].estimator

        self.explainer = shap.TreeExplainer(base_model)
        logger.info("SHAP explainer loaded successfully.")

    def generate_explanations(
        self, feature_vector_df, predicted_class_idx, feature_names
    ):
        """
        Generate SHAP values for the specific predicted class and return the top 5-10 most impactful features.
        """
        if self.explainer is None:
            return []

        # Generate SHAP values
        shap_values = self.explainer.shap_values(feature_vector_df)

        # For multi-class XGBoost, shap_values is a list of arrays (one per class)
        if isinstance(shap_values, list):
            class_shap_values = shap_values[predicted_class_idx][0]
        elif len(shap_values.shape) == 3:
            # shap >= 0.40 format: (num_samples, num_features, num_classes)
            class_shap_values = shap_values[0, :, predicted_class_idx]
        else:
            class_shap_values = shap_values[0]

        # Map to feature names
        feature_impacts = []
        for i, feature in enumerate(feature_names):
            val = feature_vector_df.iloc[0, i]
            impact = class_shap_values[i]
            direction = (
                "positive" if impact > 0 else "negative" if impact < 0 else "neutral"
            )

            # Format feature name for display
            display_name = feature.replace("_", " ").title()
            display_name = display_name.replace("L5", "(Last 5)").replace(
                "H2H", "Head-to-Head"
            )

            feature_impacts.append(
                {
                    "feature": display_name,
                    "raw_feature": feature,
                    "value": round(float(val), 2),
                    "impact": round(float(impact), 3),
                    "direction": direction,
                    "abs_impact": abs(float(impact)),
                }
            )

        # Sort by absolute impact and take top 7
        feature_impacts.sort(key=lambda x: x["abs_impact"], reverse=True)
        top_features = feature_impacts[:7]

        # Clean up keys before returning
        for f in top_features:
            del f["abs_impact"]
            del f["raw_feature"]

        return top_features

    def generate_insights(self, home_features, away_features, h2h_features):
        """
        Generate dynamic readable football insights by comparing home and away features.
        """
        insights = []

        # 1. Streaks
        hw_streak = home_features.get("home_winning_streak", 0)
        aw_streak = away_features.get("away_winning_streak", 0)

        if hw_streak >= 3:
            insights.append(f"Home team has won {int(hw_streak)} consecutive matches.")
        elif aw_streak >= 3:
            insights.append(
                f"Away team enters on a strong {int(aw_streak)}-match winning streak."
            )

        hu_streak = home_features.get("home_unbeaten_streak", 0)
        if hu_streak >= 5 and hw_streak < 3:
            insights.append(
                f"Home team is solid, carrying a {int(hu_streak)}-match unbeaten streak."
            )

        # 2. Expected Goals (xG)
        home_xg = home_features.get("home_avg_xg_l5", 0)
        away_xg = away_features.get("away_avg_xg_l5", 0)

        if home_xg > away_xg + 0.6:
            insights.append(
                f"Home side generates significantly higher attacking threat (xG: {home_xg:.2f} vs {away_xg:.2f})."
            )
        elif away_xg > home_xg + 0.6:
            insights.append(
                f"Away team has a noticeably superior expected goals average ({away_xg:.2f} per game)."
            )

        # 3. Defensive Leaks
        home_xga = home_features.get("home_avg_goals_conceded_l5", 0)
        away_xga = away_features.get("away_avg_goals_conceded_l5", 0)

        if away_xga >= 2.0:
            insights.append(
                f"Away team has been defensively vulnerable, conceding {away_xga:.1f} goals per game recently."
            )
        if home_xga >= 2.0:
            insights.append(
                f"Home team defense is struggling, allowing {home_xga:.1f} goals per match."
            )

        # 4. H2H Domination
        h2h_hw = h2h_features.get("h2h_home_wins", 0)
        h2h_aw = h2h_features.get("h2h_away_wins", 0)

        if h2h_hw > h2h_aw + 1 and h2h_hw >= 2:
            insights.append(
                "The home team has historically dominated recent head-to-head meetings."
            )
        elif h2h_aw > h2h_hw + 1 and h2h_aw >= 2:
            insights.append(
                "The away team holds a strong psychological edge in recent head-to-head fixtures."
            )

        # 5. Clean Sheets
        home_cs = home_features.get("home_clean_sheets_l5", 0)
        if home_cs >= 3:
            insights.append(
                f"Home team boasts a sturdy defense with {int(home_cs)} clean sheets in their last 5."
            )

        # Fallback if too few insights
        if len(insights) == 0:
            insights.append(
                "Both teams are relatively evenly matched in recent statistical metrics."
            )
            insights.append(
                "This fixture could be highly contested based on current form."
            )

        return insights[:4]  # Return up to 4 top insights


explainability_service = ExplainabilityService()
