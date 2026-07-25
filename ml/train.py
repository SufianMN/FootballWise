"""
train.py

Prepares the features dataset and orchestrates the advanced ML pipeline, including:
- Chronological TimeSeriesSplit
- Optional Feature Selection
- Hyperparameter tuning using RandomizedSearchCV
- Probability Calibration (Platt scaling vs Isotonic)
- Comprehensive evaluation metrics & visual reports
- Versioned model artifacts
"""

import os
import glob
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier

from .config import FEATURES_DIR, BASE_DIR
from .feature_selection import perform_feature_selection
from .hyperparameter_search import perform_hyperparameter_search
from .calibration import perform_calibration
from .training_report import generate_training_report
from .visualizations import generate_visualizations
from .evaluate import evaluate_model

MODELS_DIR = os.path.join(BASE_DIR, "models")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

def get_next_version(models_dir: str) -> str:
    """Finds the next version number based on existing models."""
    existing = glob.glob(os.path.join(models_dir, "xgboost_model_v*.joblib"))
    if not existing:
        return "v1"
    
    versions = []
    for f in existing:
        try:
            # Extract number from 'xgboost_model_vX.joblib'
            v_str = os.path.basename(f).split('_v')[1].split('.joblib')[0]
            versions.append(int(v_str))
        except (IndexError, ValueError):
            pass
            
    next_v = max(versions) + 1 if versions else 1
    return f"v{next_v}"

def preprocess_and_train():
    dataset_path = os.path.join(FEATURES_DIR, "match_dataset.csv")
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset not found at {dataset_path}")
        return
        
    print("Loading dataset...")
    df = pd.read_csv(dataset_path)
    
    # Sort chronologically to respect TimeSeriesSplit
    if 'match_date' in df.columns:
        df['match_date'] = pd.to_datetime(df['match_date'])
        df = df.sort_values('match_date').reset_index(drop=True)
    
    # 1. Remove non-feature columns
    cols_to_drop = ['match_id', 'match_date', 'home_team_id', 'away_team_id', 'competition_id', 'season_id']
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors='ignore')
    
    # 2. Handle missing values
    df = df.fillna(0)
    
    # 3. Label encode the target variable
    X = df.drop(columns=['result'])
    y_raw = df['result']
    
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y_raw)
    
    print(f"Target classes encoded as: {dict(enumerate(label_encoder.classes_))}")
    print(f"Initial Dataset shape: {X.shape}")
    
    # Set up chronological split (avoid data leakage from the future)
    tscv = TimeSeriesSplit(n_splits=5)
    
    # 4. Automatic Feature Selection
    X_selected, mask = perform_feature_selection(X, y, tscv)
    
    # 5. Hyperparameter Optimization
    best_estimator, best_params = perform_hyperparameter_search(X_selected, y, tscv)
    
    # 6. Probability Calibration
    calibrated_model, calibration_method = perform_calibration(best_estimator, X_selected, y, tscv)
    
    # 7. Final Evaluation
    print("\n" + "="*50)
    print("FINAL EVALUATION ON HOLDOUT SET")
    print("="*50)
    
    # Evaluate on the last fold to mimic predicting the future
    splits = list(tscv.split(X_selected))
    train_idx, test_idx = splits[-1]
    X_train, X_test = X_selected.iloc[train_idx], X_selected.iloc[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    
    calibrated_model.fit(X_train, y_train)
    y_pred_train = calibrated_model.predict(X_train)
    y_pred_test = calibrated_model.predict(X_test)
    y_prob_test = calibrated_model.predict_proba(X_test)
    
    metrics = evaluate_model(y_train, y_pred_train, y_test, y_pred_test, y_prob_test, label_encoder)
    metrics["calibration_method"] = calibration_method
    
    # Re-fit final model on ALL data before saving
    print("\nRefitting final model on complete dataset for production...")
    calibrated_model.fit(X_selected, y)
    
    version = get_next_version(MODELS_DIR)
    print(f"\nSaving artifacts as version {version}...")
    
    # 8. Visualizations
    generate_visualizations(
        model=calibrated_model,
        X=X_selected,
        y=y,
        y_pred=calibrated_model.predict(X_selected),
        y_prob=calibrated_model.predict_proba(X_selected),
        label_encoder=label_encoder,
        reports_dir=REPORTS_DIR
    )
    
    # 9. Model Persistence
    joblib.dump(calibrated_model, os.path.join(MODELS_DIR, f"xgboost_model_{version}.joblib"))
    joblib.dump(label_encoder, os.path.join(MODELS_DIR, f"label_encoder_{version}.joblib"))
    joblib.dump(X_selected.columns.tolist(), os.path.join(MODELS_DIR, f"feature_columns_{version}.joblib"))
    
    # 10. Training Report
    metrics["accuracy_test"] = metrics["accuracy"]
    report_path = generate_training_report(metrics, best_params, X_selected.columns.tolist(), version, REPORTS_DIR)
    
    # Save pointer to latest
    pointer_path = os.path.join(MODELS_DIR, "latest_model_info.json")
    import json
    with open(pointer_path, 'w') as f:
        json.dump({"latest_version": version}, f)
        
    print(f"All artifacts for {version} saved successfully.")

if __name__ == "__main__":
    preprocess_and_train()
