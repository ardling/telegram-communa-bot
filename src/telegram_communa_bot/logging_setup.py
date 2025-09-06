#!/bin/env/python3

"""Logging setup for the Telegram Communa Bot."""

import logging
import logging.config

from typing import Any


DATEFMT = "%Y-%m-%d %H:%M:%S"

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": DATEFMT
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s",
            "datefmt": DATEFMT
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "default",
            "stream": "ext://sys.stdout"
        }
    },
    "loggers": {
        "telegram_communa_bot": {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": False
        },
        "aiogram": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False
        }
    },
    "root": {
        "level": "WARNING",
        "handlers": ["console"]
    }
}


def setup_logging(logger_name: str, config: dict[str, Any] = LOGGING_CONFIG):
    """Initialize logging"""
    logging.config.dictConfig(config)
    return logging.getLogger(logger_name)

