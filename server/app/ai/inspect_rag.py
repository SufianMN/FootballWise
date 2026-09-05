import os
from pathlib import Path
import pandas as pd

def inspect():
    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    raw_dir = base_dir / "ml" / "data" / "raw"
    matches_csv = base_dir / "ml" / "data" / "processed" / "processed_matches.csv"
    chroma_dir = base_dir / "server" / "data" / "chroma_db"

    json_files = list(raw_dir.glob("events_*.json"))
    df_matches = pd.read_csv(matches_csv) if matches_csv.exists() else []

    print(f"Number of source JSON files in raw/: {len(json_files)}")
    print(f"Number of matches in processed_matches.csv: {len(df_matches)}")
    print(f"ChromaDB persistence directory: {chroma_dir}")
    print(f"ChromaDB directory exists: {chroma_dir.exists()}")
    if chroma_dir.exists():
        files = list(chroma_dir.iterdir())
        print(f"ChromaDB directory contents: {[f.name for f in files]}")

if __name__ == "__main__":
    inspect()
