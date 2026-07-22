"""
train.py

Prepares the features dataset, trains an XGBoost classifier,
and evaluates it using evaluate.py. Saves models and encoders.
"""

import os
import pandas as pd
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from .config import FEATURES_DIR, BASE_DIR
from .evaluate import evaluate_model, plot_feature_importance

MODELS_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

def preprocess_and_train():
    dataset_path = os.path.join(FEATURES_DIR, "match_dataset.csv")
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset not found at {dataset_path}")
        return
        
    print("Loading dataset...")
    df = pd.read_csv(dataset_path)
    
    # 1. Remove non-feature columns
    cols_to_drop = ['match_id', 'match_date', 'home_team_id', 'away_team_id', 'competition_id', 'season_id']
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors='ignore')
    
    # 2. Handle missing values
    # For robust XGBoost, NaNs are handled natively, but we can fill with 0 safely for these specific features.
    df = df.fillna(0)
    
    # 3. Label encode the target variable
    X = df.drop(columns=['result'])
    y_raw = df['result']
    
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y_raw)
    
    print(f"Target classes encoded as: {dict(enumerate(label_encoder.classes_))}")
    
    # 4. Train-test split (80/20, stratified)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    
    print(f"Training set: {X_train.shape}")
    print(f"Testing set:  {X_test.shape}")
    
    # 5. Train XGBoost classifier
    print("Training XGBoost classifier...")
    # Because of small dataset size in tests, we use a basic configuration
    model = XGBClassifier(
        objective='multi:softprob',
        num_class=3,
        eval_metric='mlogloss',
        random_state=42,
        early_stopping_rounds=10,
        learning_rate=0.1,
        max_depth=4,
        n_estimators=100
    )
    
    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=False
    )
    
    print("Training complete.")
    
    # 6. Evaluate
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    evaluate_model(y_train, y_pred_train, y_test, y_pred_test, label_encoder)
    plot_feature_importance(model, X.columns.tolist())
    
    # 7. Model Persistence
    print("\nSaving artifacts...")
    joblib.dump(model, os.path.join(MODELS_DIR, "xgboost_model.joblib"))
    joblib.dump(label_encoder, os.path.join(MODELS_DIR, "label_encoder.joblib"))
    joblib.dump(X.columns.tolist(), os.path.join(MODELS_DIR, "feature_columns.joblib"))
    
    print("All artifacts saved successfully to ml/models/")

if __name__ == "__main__":
    preprocess_and_train()
