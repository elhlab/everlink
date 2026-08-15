import os
import logging

from pathlib import Path

logger = logging.getLogger(__name__)

IS_DEV_ENV = os.environ.get("DEVELOPMENT", "false").lower() in {"1", "true"}
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()

BIND_HOST = os.environ.get("BIND_HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8000"))

CUSTOM_SERVICES_PATH = os.environ.get("CUSTOM_SERVICES_PATH", None)
if CUSTOM_SERVICES_PATH:
    CUSTOM_SERVICES_PATH = Path(CUSTOM_SERVICES_PATH)

    if not CUSTOM_SERVICES_PATH.is_dir():
        raise ValueError(
            f"Invalid CUSTOM_SERVICES_PATH: not a directory: {CUSTOM_SERVICES_PATH}"
        )

LOG_FILE = os.environ.get("LOG_FILE")
if LOG_FILE:
    LOG_FILE = Path(LOG_FILE)

    if not LOG_FILE.parent.exists():
        raise ValueError(
            f"Invalid LOG_FILE: parent directory does not exist: {LOG_FILE.parent}"
        )


def log_config():
    logger.debug(
        "Configuration: development=%s, bind_host=%s, port=%d, "
        "custom_services_path='%s', log_level=%s, log_file='%s'",
        IS_DEV_ENV,
        BIND_HOST,
        PORT,
        CUSTOM_SERVICES_PATH,
        LOG_LEVEL,
        LOG_FILE or "disabled",
    )
