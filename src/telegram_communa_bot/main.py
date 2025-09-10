#!/bin/env/python3
from .logging_setup import setup_logging

logger = setup_logging(__file__)

import asyncio
from dotenv import load_dotenv
from .bot import run_bot


def main():
    logger.info("Start Telegram Lobby Bot...")

    _ = load_dotenv()
    _ = asyncio.run(run_bot())
