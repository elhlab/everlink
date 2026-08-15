from .config import IS_DEV_ENV, LOG_FILE, LOG_LEVEL, BIND_HOST, PORT

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


def get_logging_config():
    handlers: list[tuple[str, dict]] = [
        (
            "console",
            {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
        ),
    ]

    if LOG_FILE is not None:
        handlers.append(
            (
                "file",
                {
                    "class": "logging.handlers.RotatingFileHandler",
                    "formatter": "default",
                    "filename": str(LOG_FILE),
                    "maxBytes": 10_000_000,
                    "backupCount": 1,
                },
            )
        )

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": LOG_FORMAT,
            },
        },
        "handlers": {name: handler for name, handler in handlers},
        "root": {
            "level": LOG_LEVEL,
            "handlers": [name for name, handler in handlers],
        },
    }


def main():
    import uvicorn

    config = get_logging_config()

    uvicorn.run(
        "everlink.server:app",
        host=BIND_HOST,
        port=PORT,
        reload=IS_DEV_ENV,
        log_level=LOG_LEVEL,
        log_config=config,
    )
