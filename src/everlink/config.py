import os
from pathlib import Path

IS_DEV_ENV = os.environ.get("DEVELOPMENT", "false").lower() == "true"
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()

BIND_HOST = os.environ.get("BIND_HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8000"))

LOG_FILE = os.environ.get("LOG_FILE")
if LOG_FILE:
    LOG_FILE = Path(LOG_FILE)

    if not LOG_FILE.parent.exists():
        raise ValueError(
            f"Invalid LOG_FILE: parent directory does not exist: {LOG_FILE.parent}"
        )
