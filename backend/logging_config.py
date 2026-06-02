"""Centralised logging configuration for the FastAPI backend.

Uses :mod:`logging.config.dictConfig` so output is consistent across
``uvicorn``, our application code, and third-party libraries, with an
optional JSON formatter suitable for production observability.
"""
from __future__ import annotations

import logging
import logging.config
import os
from typing import Any, Dict

_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


def _json_formatter() -> logging.Formatter:
    """Return a JSON formatter when ``LOG_JSON=1`` is set."""

    import json

    class JsonFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:  # noqa: D401
            payload: Dict[str, Any] = {
                "timestamp": self.formatTime(record, self.datefmt),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
            }
            if record.exc_info:
                payload["exception"] = self.formatException(record.exc_info)
            return json.dumps(payload, ensure_ascii=False)

    return JsonFormatter(datefmt=_DATE_FORMAT)


def configure_logging(level: str | int = "INFO") -> None:
    """Configure root logging exactly once.

    Honours the ``LOG_JSON`` environment variable: when set to a truthy
    value, every log record is emitted as a single-line JSON object.
    """
    use_json = os.getenv("LOG_JSON", "").lower() in {"1", "true", "yes"}

    handler: Dict[str, Any] = {
        "class": "logging.StreamHandler",
        "stream": "ext://sys.stderr",
        "level": level,
    }
    if use_json:
        handler["formatter"] = "json"
    else:
        handler["formatter"] = "standard"

    config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": _LOG_FORMAT,
                "datefmt": _DATE_FORMAT,
            },
            "json": {
                "()": "backend.logging_config._json_formatter",
                "datefmt": _DATE_FORMAT,
            },
        },
        "handlers": {"default": handler},
        "loggers": {
            "uvicorn": {"handlers": ["default"], "level": level, "propagate": False},
            "uvicorn.error": {"handlers": ["default"], "level": level, "propagate": False},
            "uvicorn.access": {"handlers": ["default"], "level": level, "propagate": False},
            "sqlalchemy.engine": {"level": "WARNING"},
            "google": {"level": "WARNING"},
            "httpx": {"level": "WARNING"},
        },
        "root": {"handlers": ["default"], "level": level},
    }
    logging.config.dictConfig(config)
