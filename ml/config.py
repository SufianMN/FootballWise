import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
FEATURES_DIR = os.path.join(DATA_DIR, "features")

# Target competitions for data ingestion
# If set to 'ALL', all available StatsBomb free competitions will be downloaded.
TARGET_COMPETITIONS = 'ALL'

def ensure_directories():
    """Ensure all required data directories exist."""
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    os.makedirs(FEATURES_DIR, exist_ok=True)

ensure_directories()
