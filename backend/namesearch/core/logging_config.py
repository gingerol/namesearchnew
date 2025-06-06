"""Logging configuration for the application."""
import logging
import logging.config
import os
from pathlib import Path
from typing import Any, Dict, Optional

from pythonjsonlogger import jsonlogger


def setup_logging(
    log_level: str = "INFO",
    log_format: str = "json",
    log_file: Optional[str] = None,
) -> None:
    """
    Set up logging configuration.

    Args:
        log_level: Logging level (e.g., 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').
        log_format: Log format ('json' or 'text').
        log_file: Optional path to log file. If not provided, logs to console.
    """
    log_handlers: Dict[str, Any] = {
        "console": {
            "class": "logging.StreamHandler",
            "level": log_level,
            "formatter": "json" if log_format == "json" else "text",
            "stream": "ext://sys.stdout",
        }
    }

    if log_file:
        # Ensure the log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_handlers["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": log_level,
            "formatter": "json" if log_format == "json" else "text",
            "filename": log_file,
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf8",
        }

    log_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
                "timestamp": True,
            },
            "text": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": log_handlers,
        "loggers": {
            "": {  # root logger
                "handlers": list(log_handlers.keys()),
                "level": log_level,
                "propagate": True,
            },
            "uvicorn": {"level": "INFO"},
            "uvicorn.error": {"level": "INFO"},
            "uvicorn.access": {"level": "INFO", "handlers": []},
        },
    }

    logging.config.dictConfig(log_config)


# Set up default logging when the module is imported
setup_logging(
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    log_format=os.getenv("LOG_FORMAT", "json"),
    log_file=os.getenv("LOG_FILE"),
)

# Create a logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
