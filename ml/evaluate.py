"""
evaluate.py

Handles evaluation of the XGBoost classifier.
Calculates metrics, generates confusion matrix, classification report,
and plots feature importances.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import confusion_matrix, classification_report

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EVAL_DIR = os.path.join(BASE_DIR, "evaluation")
os.makedirs(EVAL_DIR, exist_ok=True)

def evaluate_model(y_train, y_pred_train, y_test, y_pred_test, label_encoder):
    """Prints evaluation metrics and classification report."""
    
    print("\n" + "="*50)
    print("MODEL EVALUATION")
    print("="*50)
    
    # Accuracy
    train_acc = accuracy_score(y_train, y_pred_train)
    test_acc = accuracy_score(y_test, y_pred_test)
    
    print(f"Training Accuracy: {train_acc:.4f}")
    print(f"Testing Accuracy:  {test_acc:.4f}")
    
    # Other metrics (macro average for multi-class)
    precision = precision_score(y_test, y_pred_test, average='macro', zero_division=0)
    recall = recall_score(y_test, y_pred_test, average='macro', zero_division=0)
    f1 = f1_score(y_test, y_pred_test, average='macro', zero_division=0)
    
    print(f"Precision (Macro): {precision:.4f}")
    print(f"Recall (Macro):    {recall:.4f}")
    print(f"F1 Score (Macro):  {f1:.4f}")
    
    # Classification Report
    print("\nClassification Report:")
    target_names = label_encoder.classes_
    print(classification_report(y_test, y_pred_test, target_names=target_names, zero_division=0))
    
    # Confusion Matrix
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred_test)
    cm_df = pd.DataFrame(cm, index=target_names, columns=target_names)
    print(cm_df)
    
def plot_feature_importance(model, feature_names):
    """Plots and saves the top feature importances from XGBoost."""
    importances = model.feature_importances_
    
    # Sort features by importance
    indices = np.argsort(importances)[::-1]
    
    # Select top 15 (or all if < 15)
    top_n = min(15, len(feature_names))
    top_indices = indices[:top_n]
    top_importances = importances[top_indices]
    top_features = [feature_names[i] for i in top_indices]
    
    print("\n" + "="*50)
    print(f"TOP {top_n} MOST IMPORTANT FEATURES")
    print("="*50)
    for i in range(top_n):
        print(f"{i+1}. {top_features[i]} ({top_importances[i]:.4f})")
    
    # Plot
    plt.figure(figsize=(10, 8))
    sns.barplot(x=top_importances, y=top_features, hue=top_features, legend=False, palette="viridis")
    plt.title("Top 15 Feature Importances (XGBoost)")
    plt.xlabel("Importance Score")
    plt.ylabel("Features")
    plt.tight_layout()
    
    # Save
    filepath = os.path.join(EVAL_DIR, "feature_importance.png")
    plt.savefig(filepath, dpi=300)
    plt.close()
    
    print(f"\nFeature importance chart saved to {filepath}")
