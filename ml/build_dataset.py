"""
build_dataset.py

Orchestrator script for the FootballWise Data Ingestion and Feature Engineering Pipeline.
Executes ingestion, processing, feature engineering, and validation.
"""

import os
import pandas as pd
from .preprocessing import download_data, process_data
from .feature_engineering import engineer_features
from .config import FEATURES_DIR

def run_pipeline():
    print("="*50)
    print("FootballWise ML Data Pipeline (Milestone 2)")
    print("="*50)
    
    # Step 1 & 2: Ingestion and Preprocessing
    download_data()
    process_data()
    
    # Step 3, 4 & 5: Feature Engineering & Save
    engineer_features()
    
    # Step 6: Validation
    validate_dataset()

def validate_dataset():
    print("="*50)
    print("Dataset Validation")
    print("="*50)
    
    filepath = os.path.join(FEATURES_DIR, "match_dataset.csv")
    if not os.path.exists(filepath):
        print("Error: Dataset file not found.")
        return
        
    df = pd.read_csv(filepath)
    
    print(f"Total number of matches: {len(df)}")
    
    features = [c for c in df.columns if c not in ['match_id', 'match_date', 'home_team_id', 'away_team_id', 'competition_id', 'season_id', 'result']]
    print(f"Number of features: {len(features)}")
    
    missing = df.isnull().sum().sum()
    print(f"Total missing values: {missing}")
    
    print("\nFeature Names:")
    # Group by prefix to make it readable
    home_feats = [f for f in features if f.startswith('home_')]
    away_feats = [f for f in features if f.startswith('away_')]
    h2h_feats = [f for f in features if f.startswith('h2h_')]
    print(f" - Home Features ({len(home_feats)}): {', '.join(home_feats)}")
    print(f" - Away Features ({len(away_feats)}): {', '.join(away_feats)}")
    print(f" - H2H Features ({len(h2h_feats)}): {', '.join(h2h_feats)}")
    
    print("\nExample rows (.head()):")
    print(df.head())

if __name__ == "__main__":
    run_pipeline()
