import os
import joblib
import pandas as pd
import numpy as np

class PredictionService:
    def __init__(self):
        self.model = None
        self.label_encoder = None
        self.feature_columns = None
        self.dataset_df = None

    def load_artifacts(self):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../ml"))
        models_dir = os.path.join(base_dir, "models")
        features_dir = os.path.join(base_dir, "data/features")
        
        print("Loading ML artifacts...")
        model_path = os.path.join(models_dir, "xgboost_model.joblib")
        le_path = os.path.join(models_dir, "label_encoder.joblib")
        fc_path = os.path.join(models_dir, "feature_columns.joblib")
        
        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
        if os.path.exists(le_path):
            self.label_encoder = joblib.load(le_path)
        if os.path.exists(fc_path):
            self.feature_columns = joblib.load(fc_path)
            
        dataset_path = os.path.join(features_dir, "match_dataset.csv")
        if os.path.exists(dataset_path):
            self.dataset_df = pd.read_csv(dataset_path)

    def _get_latest_team_features(self, team_id, prefix="home"):
        # We need to extract this team's latest rolling stats and map them to the requested prefix
        tid = float(team_id)
        team_home = self.dataset_df[self.dataset_df['home_team_id'] == tid]
        team_away = self.dataset_df[self.dataset_df['away_team_id'] == tid]
        
        latest_home = team_home.sort_values(by='match_date', ascending=False).iloc[0] if len(team_home) > 0 else None
        latest_away = team_away.sort_values(by='match_date', ascending=False).iloc[0] if len(team_away) > 0 else None
        
        latest_row = None
        was_home = True
        
        if latest_home is not None and latest_away is not None:
            if latest_home['match_date'] >= latest_away['match_date']:
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
            return {} # Team not found
            
        source_prefix = "home_" if was_home else "away_"
        
        # Extract all features that start with source_prefix and rename them to prefix
        features = {}
        for col in self.feature_columns:
            if col.startswith(prefix + "_"):
                suffix = col[len(prefix + "_"):]
                source_col = f"{source_prefix}{suffix}"
                
                # Special cases where the suffix doesn't perfectly match (e.g., home_home_win_rate)
                # But actually, home_home_win_rate means home team's win rate at home.
                # If they were away last time, their away_home_win_rate has it.
                if source_col in latest_row:
                    features[col] = latest_row[source_col]
                else:
                    features[col] = 0.0
                    
        return features
        
    def _get_h2h_features(self, home_team_id, away_team_id):
        tid1, tid2 = float(home_team_id), float(away_team_id)
        # Search for matches in either orientation
        h2h_matches = self.dataset_df[
            ((self.dataset_df['home_team_id'] == tid1) & (self.dataset_df['away_team_id'] == tid2)) |
            ((self.dataset_df['home_team_id'] == tid2) & (self.dataset_df['away_team_id'] == tid1))
        ]
        
        if len(h2h_matches) > 0:
            latest = h2h_matches.sort_values(by='match_date', ascending=False).iloc[0]
            features = {}
            
            # Check if historical orientation matches the current prediction
            is_same_orientation = (latest['home_team_id'] == tid1)
            
            for col in self.feature_columns:
                if col.startswith("h2h_"):
                    if col == 'h2h_home_wins':
                        features[col] = latest['h2h_home_wins'] if is_same_orientation else latest['h2h_away_wins']
                    elif col == 'h2h_away_wins':
                        features[col] = latest['h2h_away_wins'] if is_same_orientation else latest['h2h_home_wins']
                    else:
                        features[col] = latest[col] if col in latest else 0.0
            return features
            
        return {col: 0.0 for col in self.feature_columns if col.startswith("h2h_")}

    def predict(self, home_team_id, away_team_id):
        if not self.model or not self.dataset_df is not None:
            raise ValueError("Model or dataset not loaded")
            
        if home_team_id == away_team_id:
            raise ValueError("Home and Away teams must be different")
            
        home_features = self._get_latest_team_features(home_team_id, "home")
        away_features = self._get_latest_team_features(away_team_id, "away")
        h2h_features = self._get_h2h_features(home_team_id, away_team_id)
        
        if not home_features or not away_features:
            raise ValueError("Could not find sufficient historical data for the selected teams")
            
        # Combine features
        combined = {**home_features, **away_features, **h2h_features}
        
        # Ensure correct column ordering
        vector = []
        for col in self.feature_columns:
            vector.append(combined.get(col, 0.0))
            
        # Predict
        X = pd.DataFrame([vector], columns=self.feature_columns)
        
        probabilities = self.model.predict_proba(X)[0]
        predicted_idx = np.argmax(probabilities)
        predicted_label = self.label_encoder.inverse_transform([predicted_idx])[0]
        
        # label_encoder classes are typically ['Away Win', 'Draw', 'Home Win']
        # Let's dynamically map them
        classes = list(self.label_encoder.classes_)
        
        res = {
            "predicted_result": predicted_label,
            "confidence": round(float(probabilities[predicted_idx]) * 100, 1)
        }
        
        for i, cls in enumerate(classes):
            key = cls.lower().replace(" ", "_") + "_probability"
            res[key] = round(float(probabilities[i]), 2)
            
        # Add Explainability
        from .explainability_service import explainability_service
        
        # We need predicted_idx as a standard int, np.argmax might return numpy.int64
        top_features = explainability_service.generate_explanations(X, int(predicted_idx), self.feature_columns)
        insights = explainability_service.generate_insights(home_features, away_features, h2h_features)
        
        res["top_features"] = top_features
        res["insights"] = insights
            
        return res

prediction_service = PredictionService()
