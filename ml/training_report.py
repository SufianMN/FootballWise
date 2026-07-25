import json
import os
import datetime

def generate_training_report(metrics: dict, params: dict, features: list, version: str, reports_dir: str):
    """
    Saves a comprehensive JSON report containing all metrics and parameters
    for a specific training run.
    """
    os.makedirs(reports_dir, exist_ok=True)
    
    report = {
        "training_date": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "version": version,
        "feature_count": len(features),
        "selected_features": features,
        "best_parameters": params,
        "metrics": metrics
    }
    
    filepath = os.path.join(reports_dir, f"training_report_{version}.json")
    with open(filepath, 'w') as f:
        json.dump(report, f, indent=4)
        
    print(f"\nTraining report saved to {filepath}")
    return filepath
