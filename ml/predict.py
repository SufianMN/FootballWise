"""
predict.py

Provides a standalone prediction module. 
Loads the saved XGBoost model, label encoder, and feature columns 
to provide match outcome predictions for a given set of features.
"""

import os
import joblib
import pandas as pd
from .config import BASE_DIR

MODELS_DIR = os.path.join(BASE_DIR, "models")

# We use global variables to cache the model in memory so that
# the FastAPI backend can import this module and keep the model hot.
_MODEL = None
_LABEL_ENCODER = None
_FEATURE_COLUMNS = None

def load_artifacts():
    global _MODEL, _LABEL_ENCODER, _FEATURE_COLUMNS
    if _MODEL is None:
        model_path = os.path.join(MODELS_DIR, "xgboost_model.joblib")
        le_path = os.path.join(MODELS_DIR, "label_encoder.joblib")
        cols_path = os.path.join(MODELS_DIR, "feature_columns.joblib")
        
        if not all(os.path.exists(p) for p in [model_path, le_path, cols_path]):
            raise FileNotFoundError("Model artifacts not found. Please run ml/train.py first.")
            
        _MODEL = joblib.load(model_path)
        _LABEL_ENCODER = joblib.load(le_path)
        _FEATURE_COLUMNS = joblib.load(cols_path)
        
def predict_match(features: dict) -> dict:
    """
    Accepts a dictionary of feature values, aligns them with the trained model's
    expected feature columns, and returns outcome probabilities.
    """
    load_artifacts()
    
    # Align features with expected columns, defaulting missing features to 0
    aligned_features = {col: features.get(col, 0) for col in _FEATURE_COLUMNS}
    
    df = pd.DataFrame([aligned_features])
    
    # Predict probabilities
    probs = _MODEL.predict_proba(df)[0]
    
    # The label encoder dictates which index corresponds to which outcome
    classes = _LABEL_ENCODER.classes_
    prob_dict = {classes[i]: float(probs[i]) for i in range(len(classes))}
    
    # Determine predicted result (argmax)
    predicted_class_idx = probs.argmax()
    predicted_result = classes[predicted_class_idx]
    
    return {
        "home_win_probability": prob_dict.get("Home Win", 0.0),
        "draw_probability": prob_dict.get("Draw", 0.0),
        "away_win_probability": prob_dict.get("Away Win", 0.0),
        "predicted_result": predicted_result
    }

if __name__ == "__main__":
    # Local Testing Script
    print("Testing inference module...")
    
    # Provide dummy mock data for testing (all zeros)
    load_artifacts()
    dummy_features = {col: 0.5 for col in _FEATURE_COLUMNS}
    
    result = predict_match(dummy_features)
    print("Inference successful. Output:")
    print(result)
