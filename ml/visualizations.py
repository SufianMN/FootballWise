import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, roc_curve, auc
from sklearn.calibration import calibration_curve
import shap

def generate_visualizations(model, X: pd.DataFrame, y: np.ndarray, y_pred, y_prob, label_encoder, reports_dir: str):
    """Generates and saves all requested visualizations."""
    os.makedirs(reports_dir, exist_ok=True)
    target_names = label_encoder.classes_
    
    # 1. Confusion Matrix
    cm = confusion_matrix(y, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=target_names, yticklabels=target_names)
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(os.path.join(reports_dir, "confusion_matrix.png"), dpi=300)
    plt.close()
    
    # 2. ROC Curve (One-vs-Rest)
    plt.figure(figsize=(10, 8))
    for i, class_name in enumerate(target_names):
        y_true_binary = (y == i).astype(int)
        fpr, tpr, _ = roc_curve(y_true_binary, y_prob[:, i])
        roc_auc = auc(fpr, tpr)
        plt.plot(fpr, tpr, lw=2, label=f'ROC curve of class {class_name} (area = {roc_auc:.2f})')
        
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic (One-vs-Rest)')
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(os.path.join(reports_dir, "roc_curve.png"), dpi=300)
    plt.close()
    
    # 3. Calibration Curve (Reliability Diagram)
    plt.figure(figsize=(10, 10))
    ax1 = plt.subplot2grid((3, 1), (0, 0), rowspan=2)
    ax2 = plt.subplot2grid((3, 1), (2, 0))
    
    ax1.plot([0, 1], [0, 1], "k:", label="Perfectly calibrated")
    for i, class_name in enumerate(target_names):
        prob_true, prob_pred = calibration_curve((y == i).astype(int), y_prob[:, i], n_bins=10)
        ax1.plot(prob_pred, prob_true, "s-", label=f"{class_name}")
        ax2.hist(y_prob[:, i], range=(0, 1), bins=10, label=f"{class_name}", histtype="step", lw=2)
        
    ax1.set_ylabel("Fraction of positives")
    ax1.set_ylim([-0.05, 1.05])
    ax1.legend(loc="lower right")
    ax1.set_title('Calibration Plots (Reliability Curve)')
    
    ax2.set_xlabel("Mean predicted value")
    ax2.set_ylabel("Count")
    ax2.legend(loc="upper center", ncol=3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(reports_dir, "calibration_curve.png"), dpi=300)
    plt.close()
    
    # 4. Feature Importance
    # Handle CalibratedClassifierCV wrapping
    base_model = model
    if hasattr(model, 'calibrated_classifiers_'):
        base_model = model.calibrated_classifiers_[0].estimator
    
    if hasattr(base_model, 'feature_importances_'):
        importances = base_model.feature_importances_
        indices = np.argsort(importances)[::-1]
        top_n = min(25, len(X.columns))
        top_indices = indices[:top_n]
        top_importances = importances[top_indices]
        top_features = [X.columns[i] for i in top_indices]
        
        plt.figure(figsize=(12, 10))
        sns.barplot(x=top_importances, y=top_features, hue=top_features, legend=False, palette="viridis")
        plt.title("Top 25 Feature Importances (Gain)")
        plt.xlabel("Importance Score")
        plt.ylabel("Features")
        plt.tight_layout()
        plt.savefig(os.path.join(reports_dir, "feature_importance.png"), dpi=300)
        plt.close()
    
    # 5. SHAP Summary
    try:
        explainer = shap.TreeExplainer(base_model)
        # Calculate SHAP values on a sample to save time if dataset is huge
        X_sample = X.sample(n=min(2000, len(X)), random_state=42)
        shap_values = explainer.shap_values(X_sample)
        
        plt.figure()
        # SHAP returns a list of arrays for multi-class. We plot the summary for class 1 (usually Home Win)
        shap.summary_plot(shap_values, X_sample, show=False)
        plt.tight_layout()
        plt.savefig(os.path.join(reports_dir, "shap_summary.png"), dpi=300)
        plt.close()
    except Exception as e:
        print(f"Failed to generate SHAP summary plot: {e}")

