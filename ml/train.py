"""
train.py

Prepares the features dataset, optimizes XGBoost hyperparameters using RandomizedSearchCV 
with Stratified K-Fold cross-validation, and saves the best model and encoders.
"""

import os
import pandas as pd
import numpy as np
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import StratifiedKFold, RandomizedSearchCV
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, log_loss
from .config import FEATURES_DIR, BASE_DIR
from .evaluate import plot_feature_importance

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
    df = df.fillna(0)
    
    # 3. Label encode the target variable
    X = df.drop(columns=['result'])
    y_raw = df['result']
    
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y_raw)
    
    print(f"Target classes encoded as: {dict(enumerate(label_encoder.classes_))}")
    print(f"Dataset shape: {X.shape}")
    
    # 4. Hyperparameter Tuning with RandomizedSearchCV
    print("Setting up RandomizedSearchCV with StratifiedKFold...")
    
    # Define parameter grid
    param_grid = {
        'max_depth': [3, 4, 5, 6, 7],
        'learning_rate': [0.01, 0.05, 0.1, 0.2],
        'n_estimators': [100, 200, 300, 500],
        'subsample': [0.6, 0.8, 1.0],
        'colsample_bytree': [0.6, 0.8, 1.0],
        'min_child_weight': [1, 3, 5],
        'gamma': [0, 0.1, 0.5, 1, 5]
    }
    
    base_model = XGBClassifier(
        objective='multi:softprob',
        num_class=3,
        random_state=42,
        eval_metric='mlogloss'
    )
    
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    random_search = RandomizedSearchCV(
        estimator=base_model,
        param_distributions=param_grid,
        n_iter=20,  # Number of random parameter combinations to try
        scoring='neg_log_loss',
        cv=skf,
        verbose=1,
        random_state=42,
        n_jobs=-1
    )
    
    print("Running hyperparameter search. This may take a few minutes...")
    random_search.fit(X, y)
    
    print("\nBest parameters found:")
    print(random_search.best_params_)
    print(f"Best CV Log Loss: {-random_search.best_score_:.4f}")
    
    best_model = random_search.best_estimator_
    
    # 5. Cross-Validation Metrics on best model
    print("\nCalculating metrics across folds using the best model...")
    acc_scores, prec_scores, rec_scores, f1_scores, logloss_scores = [], [], [], [], []
    
    for train_idx, test_idx in skf.split(X, y):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        # Clone model to prevent data leakage across folds
        clone_model = XGBClassifier(**best_model.get_params())
        clone_model.fit(X_train, y_train)
        
        y_pred = clone_model.predict(X_test)
        y_prob = clone_model.predict_proba(X_test)
        
        acc_scores.append(accuracy_score(y_test, y_pred))
        prec_scores.append(precision_score(y_test, y_pred, average='macro', zero_division=0))
        rec_scores.append(recall_score(y_test, y_pred, average='macro', zero_division=0))
        f1_scores.append(f1_score(y_test, y_pred, average='macro', zero_division=0))
        logloss_scores.append(log_loss(y_test, y_prob))
        
    print("\n" + "="*50)
    print("CROSS-VALIDATION RESULTS (Averages)")
    print("="*50)
    print(f"Accuracy:      {np.mean(acc_scores):.4f} (+/- {np.std(acc_scores):.4f})")
    print(f"Precision:     {np.mean(prec_scores):.4f} (+/- {np.std(prec_scores):.4f})")
    print(f"Recall:        {np.mean(rec_scores):.4f} (+/- {np.std(rec_scores):.4f})")
    print(f"F1 Score:      {np.mean(f1_scores):.4f} (+/- {np.std(f1_scores):.4f})")
    print(f"Log Loss:      {np.mean(logloss_scores):.4f} (+/- {np.std(logloss_scores):.4f})")
    
    # 6. Final Evaluation & Feature Importance
    # We use the best model trained on the full dataset (random_search.best_estimator_ does this automatically)
    plot_feature_importance(best_model, X.columns.tolist())
    
    # 7. Model Persistence
    print("\nSaving artifacts...")
    joblib.dump(best_model, os.path.join(MODELS_DIR, "xgboost_model.joblib"))
    joblib.dump(label_encoder, os.path.join(MODELS_DIR, "label_encoder.joblib"))
    joblib.dump(X.columns.tolist(), os.path.join(MODELS_DIR, "feature_columns.joblib"))
    
    print("All artifacts saved successfully to ml/models/")

if __name__ == "__main__":
    preprocess_and_train()
