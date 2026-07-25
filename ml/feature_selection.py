import numpy as np
from sklearn.feature_selection import SelectFromModel
from xgboost import XGBClassifier
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import log_loss
import pandas as pd

def perform_feature_selection(X: pd.DataFrame, y: np.ndarray, tscv: TimeSeriesSplit):
    """
    Evaluates whether reducing features via SelectFromModel improves or maintains 
    cross-validated Log Loss.
    Returns (selected_X, mask) where mask is a boolean array of kept features.
    """
    print("\n" + "="*50)
    print("AUTOMATIC FEATURE SELECTION")
    print("="*50)
    
    base_model = XGBClassifier(
        objective='multi:softprob',
        num_class=3,
        random_state=42,
        eval_metric='mlogloss',
        n_estimators=100
    )
    
    # 1. Baseline Evaluation
    print(f"Evaluating baseline with all {X.shape[1]} features...")
    baseline_log_losses = []
    
    for train_idx, val_idx in tscv.split(X):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]
        
        base_model.fit(X_train, y_train)
        y_prob = base_model.predict_proba(X_val)
        baseline_log_losses.append(log_loss(y_val, y_prob))
        
    baseline_score = np.mean(baseline_log_losses)
    print(f"Baseline Log Loss: {baseline_score:.4f}")
    
    # 2. Feature Selection
    print("Fitting SelectFromModel...")
    # Fit on entire dataset to find global feature importances for selection
    base_model.fit(X, y)
    selector = SelectFromModel(base_model, prefit=True)
    mask = selector.get_support()
    
    X_reduced = X.loc[:, mask]
    num_selected = X_reduced.shape[1]
    print(f"Features selected: {num_selected} out of {X.shape[1]}")
    
    if num_selected == X.shape[1]:
        print("No features were removed.")
        return X, np.ones(X.shape[1], dtype=bool)
        
    if num_selected == 0:
        print("Selector removed all features! Falling back to original features.")
        return X, np.ones(X.shape[1], dtype=bool)
        
    # 3. Reduced Evaluation
    print(f"Evaluating reduced model with {num_selected} features...")
    reduced_log_losses = []
    
    for train_idx, val_idx in tscv.split(X_reduced):
        X_train, X_val = X_reduced.iloc[train_idx], X_reduced.iloc[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]
        
        base_model.fit(X_train, y_train)
        y_prob = base_model.predict_proba(X_val)
        reduced_log_losses.append(log_loss(y_val, y_prob))
        
    reduced_score = np.mean(reduced_log_losses)
    print(f"Reduced Log Loss: {reduced_score:.4f}")
    
    # 4. Decision
    # We keep reduced if log loss is better (lower) or very close (e.g., within 0.005)
    # to encourage simpler models.
    threshold = 0.005
    if reduced_score <= baseline_score + threshold:
        print(f"ACCEPTING reduced feature set (diff: {reduced_score - baseline_score:+.4f})")
        return X_reduced, mask
    else:
        print(f"REJECTING reduced feature set (diff: {reduced_score - baseline_score:+.4f}). Too much information lost.")
        return X, np.ones(X.shape[1], dtype=bool)
