import logging
import os
import sys

# --- Environment Settings ---
# Use os.environ.get for security, avoiding hardcoded secrets.
PLAYER_ID = os.environ.get("PLAYER_ID", "2d83fbb5-6f52-4009-8f4a-c5a9fcc391c2")
BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

# --- Game Settings ---
VENUE_CAPACITY = 1000

# --- Logging Configuration ---
def setup_logging():
    """Sets up a structured logger."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] - %(message)s",
        stream=sys.stdout,
    )
