import logging
import logging.config
from pathlib import Path


_LOG_FILE_PATH = Path(__file__).resolve().parents[2] / "app.log"


def build_logging():

    dict_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s | %(levelname)-s | %(name)s | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stderr",
                "level": "INFO",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": str(_LOG_FILE_PATH),
                "encoding": "utf-8",
                "formatter": "default",
                "maxBytes": 5_000_000,
                "backupCount": 2,
                "level": "DEBUG",
            },
        },
        "root": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
        },
        "loggers": {
            # Controls all anki_collection_scanner.* loggers in one place.
            # Set to DEBUG to allow module-level debug logs through to the file handler.
            "anki_collection_scanner": {
                "level": "DEBUG",
                "propagate": True,
            },
            # Suppress urllib3 noise below WARNING; let root route it to both handlers.
            "urllib3": {
                "level": "WARNING",
                "propagate": True,
            },
        },
    }

    logging.config.dictConfig(dict_config)

