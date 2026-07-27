import logging
import os

from dotenv import load_dotenv

# Load env variables if present
load_dotenv()

# Determine log level from environment
log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
log_level = getattr(logging, log_level_str, logging.INFO)

# Configure the basic logging settings
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def get_logger(name: str):
    """Return a logger instance with the specified name."""
    return logging.getLogger(name)
