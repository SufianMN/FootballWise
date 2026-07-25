"""
evaluate.py

Handles evaluation of the XGBoost classifier.
Calculates extended metrics including ECE, MCE, Brier Score, and Log Loss.
"""

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    balanced_accuracy_score, log_loss, brier_score_loss, classification_report
)
from sklearn.calibration import calibration_curve

def expected_calibration_error(y_true, y_prob, n_bins=10):
    """Calculates ECE (Expected Calibration Error)."""
    ece = 0.0
    for i in range(y_prob.shape[1]):
        prob_true, prob_pred = calibration_curve((y_true == i).astype(int), y_prob[:, i], n_bins=n_bins)
        # Weight by bin size - calibration_curve doesn't return bin counts natively so this is a simplified ECE
        # A more precise ECE would bin manually and weight by exact sample count.
        ece += np.mean(np.abs(prob_true - prob_pred))
    return ece / y_prob.shape[1]

def maximum_calibration_error(y_true, y_prob, n_bins=10):
    """Calculates MCE (Maximum Calibration Error)."""
    mce = 0.0
    for i in range(y_prob.shape[1]):
        prob_true, prob_pred = calibration_curve((y_true == i).astype(int), y_prob[:, i], n_bins=n_bins)
        if len(prob_true) > 0:
            mce = max(mce, np.max(np.abs(prob_true - prob_pred)))
    return mce

def evaluate_model(y_train, y_pred_train, y_test, y_pred_test, y_prob_test, label_encoder):
    """Prints evaluation metrics, classification report, and returns a metrics dictionary."""
    
    # 1. Standard Metrics
    train_acc = accuracy_score(y_train, y_pred_train)
    test_acc = accuracy_score(y_test, y_pred_test)
    balanced_acc = balanced_accuracy_score(y_test, y_pred_test)
    
    precision = precision_score(y_test, y_pred_test, average='macro', zero_division=0)
    recall = recall_score(y_test, y_pred_test, average='macro', zero_division=0)
    f1 = f1_score(y_test, y_pred_test, average='macro', zero_division=0)
    
    # 2. Probability Metrics
    logloss = log_loss(y_test, y_prob_test)
    
    # Average Brier score across classes
    brier = np.mean([brier_score_loss((y_test == c).astype(int), y_prob_test[:, c]) for c in range(len(label_encoder.classes_))])
    
    # 3. Calibration Metrics
    ece = expected_calibration_error(y_test, y_prob_test)
    mce = maximum_calibration_error(y_test, y_prob_test)
    
    print(f"Training Accuracy:   {train_acc:.4f}")
    print(f"Testing Accuracy:    {test_acc:.4f}")
    print(f"Balanced Accuracy:   {balanced_acc:.4f}")
    print(f"Precision (Macro):   {precision:.4f}")
    print(f"Recall (Macro):      {recall:.4f}")
    print(f"F1 Score (Macro):    {f1:.4f}")
    print(f"Log Loss:            {logloss:.4f}")
    print(f"Brier Score (Mean):  {brier:.4f}")
    print(f"Expected Calib Err:  {ece:.4f}")
    print(f"Max Calib Err:       {mce:.4f}")
    
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred_test, target_names=label_encoder.classes_, zero_division=0))
    
    return {
        "accuracy": test_acc,
        "balanced_accuracy": balanced_acc,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "log_loss": logloss,
        "brier_score": brier,
        "expected_calibration_error": ece,
        "maximum_calibration_error": mce
    }
