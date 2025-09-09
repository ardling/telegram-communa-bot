#!/bin/env/python3

from telegram_communa_bot.logging_setup import setup_logging


def test_logging_setup():
    """Test that logging setup initializes correctly."""
    logger = setup_logging(__file__)
    assert logger is not None
