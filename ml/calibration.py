import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import brier_score_loss, log_loss

def perform_calibration(base_estimator, X: pd.DataFrame, y: np.ndarray, tscv):
    """
    Evaluates Platt scaling ('sigmoid') vs 'isotonic' calibration on the last 
    chronological hold-out set, and returns a CalibratedClassifierCV fitted on the 
    entire dataset using the best method.
    """
    print("\n" + "="*50)
    print("PROBABILITY CALIBRATION")
    print("="*50)
    
    # We will use the last split for evaluating calibration methods
    splits = list(tscv.split(X))
    train_idx, val_idx = splits[-1]
    
    X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
    y_train, y_val = y[train_idx], y[val_idx]
    
    # Fit the base estimator on the train split
    base_estimator.fit(X_train, y_train)
    uncalibrated_probs = base_estimator.predict_proba(X_val)
    
    # 1. Uncalibrated Baseline Brier Score
    uncal_brier = np.mean([brier_score_loss((y_val == c).astype(int), uncalibrated_probs[:, c]) for c in range(3)])
    print(f"Uncalibrated Brier Score: {uncal_brier:.4f}")
    
    methods = ['sigmoid', 'isotonic']
    best_method = None
    best_brier = uncal_brier
    
    for method in methods:
        print(f"Testing {method} calibration...")
        # Since base_estimator is already fitted on X_train, we use 'prefit' to test calibration on X_val
        try:
            calibrator = CalibratedClassifierCV(estimator=base_estimator, method=method, cv='prefit')
            calibrator.fit(X_val, y_val)
            cal_probs = calibrator.predict_proba(X_val)
        except Exception as e:
            # Fallback if 'prefit' fails in some sklearn environments
            print(f"  Prefit failed, refitting calibrator with cv=3 on validation subset...")
            calibrator = CalibratedClassifierCV(estimator=base_estimator, method=method, cv=3)
            calibrator.fit(X_val, y_val)
            cal_probs = calibrator.predict_proba(X_val)
            
        brier = np.mean([brier_score_loss((y_val == c).astype(int), cal_probs[:, c]) for c in range(3)])
        print(f"  {method} Brier Score: {brier:.4f}")
        
        if brier < best_brier:
            best_brier = brier
            best_method = method
            
    if best_method is None:
        print("Calibration did not improve Brier score. Falling back to uncalibrated.")
        base_estimator.fit(X, y)
        return base_estimator, 'none'
    else:
        print(f"Selecting {best_method} calibration (Brier: {best_brier:.4f})")
        # Final model fit on full data using cv=tscv which splits internally to calibrate
        final_calibrator = CalibratedClassifierCV(estimator=base_estimator, method=best_method, cv=tscv)
        final_calibrator.fit(X, y)
        return final_calibrator, best_method
