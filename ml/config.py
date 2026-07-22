import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
FEATURES_DIR = os.path.join(DATA_DIR, "features")

# Selected free competitions for building the dataset
# Premier League 2003/2004 (2: 44)
# La Liga 2020/2021 (11: 90)
TARGET_COMPETITIONS = {
    2: [44]       # Premier League 2003/2004 (Invincibles)
}

def ensure_directories():
    """Ensure all required data directories exist."""
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    os.makedirs(FEATURES_DIR, exist_ok=True)

ensure_directories()
