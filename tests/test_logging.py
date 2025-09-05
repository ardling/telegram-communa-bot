#!/bin/env/python3

import logging
import tempfile
import os
from unittest.mock import patch
from telegram_communa_bot.logging_setup import setup_logging
from telegram_communa_bot.logging_config import LOGGING_CONFIG


def test_logging_setup():
    """Test that logging setup initializes correctly."""
    logger = setup_logging()
    assert logger is not None
    assert logger.name == "telegram_communa_bot"
    assert logger.level == logging.DEBUG


def test_logging_config_structure():
    """Test that logging configuration has the expected structure."""
    assert "version" in LOGGING_CONFIG
    assert "formatters" in LOGGING_CONFIG
    assert "handlers" in LOGGING_CONFIG
    assert "loggers" in LOGGING_CONFIG
    assert "root" in LOGGING_CONFIG
    
    # Check that our main logger is configured
    assert "telegram_communa_bot" in LOGGING_CONFIG["loggers"]
    

def test_logging_output():
    """Test that logging actually produces output."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Modify config to use temp directory for log file
        test_config = LOGGING_CONFIG.copy()
        test_config["handlers"]["file"]["filename"] = os.path.join(temp_dir, "test.log")
        
        with patch('telegram_communa_bot.logging_setup.LOGGING_CONFIG', test_config):
            logger = setup_logging()
            test_message = "Test logging message"
            logger.info(test_message)
            
            # Check that log file was created and contains our message
            log_file_path = test_config["handlers"]["file"]["filename"]
            assert os.path.exists(log_file_path)
            
            with open(log_file_path, 'r') as f:
                log_content = f.read()
                assert test_message in log_content