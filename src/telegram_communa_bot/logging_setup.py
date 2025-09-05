#!/bin/env/python3

"""Logging setup for the Telegram Communa Bot."""

import logging
import logging.config
from .logging_config import LOGGING_CONFIG


def setup_logging():
    """Initialize logging using the configuration from logging_config.py."""
    logging.config.dictConfig(LOGGING_CONFIG)
    
    # Return the main logger for the application
    return logging.getLogger("telegram_communa_bot")