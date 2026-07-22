import pandas as pd
import json
import os
from .config import RAW_DIR

def save_raw_json(data: dict | list, filename: str):
    """Save raw dict/list data as JSON to the raw directory."""
    filepath = os.path.join(RAW_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

def load_raw_json(filename: str):
    """Load JSON data from the raw directory."""
    filepath = os.path.join(RAW_DIR, filename)
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize DataFrame column names to lowercase and underscores."""
    df.columns = [str(c).lower().strip().replace(' ', '_').replace('.', '_') for c in df.columns]
    return df
