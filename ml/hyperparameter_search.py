import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import RandomizedSearchCV, TimeSeriesSplit

def perform_hyperparameter_search(X: pd.DataFrame, y: np.ndarray, tscv: TimeSeriesSplit):
    """
    Runs a structured hyperparameter search using RandomizedSearchCV and TimeSeriesSplit.
    Returns the best fitted estimator and its parameters.
    """
    print("\n" + "="*50)
    print("HYPERPARAMETER OPTIMIZATION")
    print("="*50)
    
    # Expanded parameter grid for more structured search
    param_grid = {
        'max_depth': [3, 4, 5, 6, 7],
        'learning_rate': [0.01, 0.05, 0.1, 0.2],
        'n_estimators': [100, 200, 300, 400, 500],
        'subsample': [0.6, 0.7, 0.8, 0.9, 1.0],
        'colsample_bytree': [0.6, 0.7, 0.8, 0.9, 1.0],
        'min_child_weight': [1, 3, 5, 7],
        'gamma': [0, 0.1, 0.2, 0.5, 1, 2, 5],
        'reg_alpha': [0, 0.1, 0.5, 1, 5],
        'reg_lambda': [1, 1.5, 2, 5, 10]
    }
    
    base_model = XGBClassifier(
        objective='multi:softprob',
        num_class=3,
        random_state=42,
        eval_metric='mlogloss'
    )
    
    random_search = RandomizedSearchCV(
        estimator=base_model,
        param_distributions=param_grid,
        n_iter=30,  # Try 30 parameter combinations
        scoring='neg_log_loss',
        cv=tscv,
        verbose=1,
        random_state=42,
        n_jobs=-1
    )
    
    print(f"Running randomized search ({random_search.n_iter} iterations) across {tscv.get_n_splits()} time-aware splits...")
    random_search.fit(X, y)
    
    print("\nBest parameters found:")
    for k, v in random_search.best_params_.items():
        print(f"  {k}: {v}")
    print(f"Best CV Log Loss: {-random_search.best_score_:.4f}")
    
    return random_search.best_estimator_, random_search.best_params_
