import os
import joblib
import pandas as pd
import numpy as np

class PredictionService:
    def __init__(self):
        self.model = None
        self.label_encoder = None
        self.feature_columns = None

    def load_model(self):
        """Wrapper to maintain backward compatibility."""
        self.load_artifacts()

    def load_artifacts(self):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../ml"))
        models_dir = os.path.join(base_dir, "models")
        
        import json
        pointer_path = os.path.join(models_dir, "latest_model_info.json")
        version = ""
        
        if os.path.exists(pointer_path):
            try:
                with open(pointer_path, 'r') as f:
                    info = json.load(f)
                    version = f"_{info.get('latest_version', '')}"
            except Exception as e:
                print(f"Warning: Could not read latest_model_info.json: {e}")
                
        print(f"Loading ML model artifacts (version {version.strip('_')} if versioned)...")
        
        # Fallback to unversioned if version info is missing or older pipeline is used
        model_path = os.path.join(models_dir, f"xgboost_model{version}.joblib")
        if not os.path.exists(model_path):
            model_path = os.path.join(models_dir, "xgboost_model.joblib")
            version = ""
            
        le_path = os.path.join(models_dir, f"label_encoder{version}.joblib")
        fc_path = os.path.join(models_dir, f"feature_columns{version}.joblib")
        
        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
        if os.path.exists(le_path):
            self.label_encoder = joblib.load(le_path)
        if os.path.exists(fc_path):
            self.feature_columns = joblib.load(fc_path)

    def predict(self, home_team_id, away_team_id):
        if not self.model:
            raise ValueError("Model not loaded")
            
        if home_team_id == away_team_id:
            raise ValueError("Home and Away teams must be different")
            
        # 1. Feature Builder
        from .feature_builder_service import feature_builder_service
        
        # Ensure data is loaded just in case (should happen at startup)
        if feature_builder_service.dataset_df is None:
            feature_builder_service.load_data()
            
        X, home_features, away_features, h2h_features = feature_builder_service.build_match_features(
            home_team_id, away_team_id, self.feature_columns
        )
        
        if X is None:
            raise ValueError("Could not find sufficient historical data for the selected teams")
            
        # 2. Predict
        probabilities = self.model.predict_proba(X)[0]
        predicted_idx = np.argmax(probabilities)
        predicted_label = self.label_encoder.inverse_transform([predicted_idx])[0]
        
        confidence = round(float(probabilities[predicted_idx]) * 100, 1)
        
        # 3. Confidence Level (Adjusted for Calibrated Probabilities)
        # Calibrated probabilities rarely reach 90%+. A true 80% prediction in football is extremely high confidence.
        if confidence >= 80:
            confidence_level = "Very High"
        elif confidence >= 65:
            confidence_level = "High"
        elif confidence >= 50:
            confidence_level = "Medium"
        else:
            confidence_level = "Low"
            
        classes = list(self.label_encoder.classes_)
        
        res = {
            "predicted_result": predicted_label,
            "confidence": confidence,
            "confidence_level": confidence_level
        }
        
        for i, cls in enumerate(classes):
            key = cls.lower().replace(" ", "_") + "_probability"
            res[key] = round(float(probabilities[i]), 2)
            
        # 4. Match Preview
        from .match_preview_service import match_preview_service
        res["match_preview"] = match_preview_service.generate_preview(home_team_id, away_team_id)
            
        # 5. Explainability
        from .explainability_service import explainability_service
        
        top_features = explainability_service.generate_explanations(X, int(predicted_idx), self.feature_columns)
        insights = explainability_service.generate_insights(home_features, away_features, h2h_features)
        
        res["top_features"] = top_features
        res["insights"] = insights
            
        return res

prediction_service = PredictionService()
