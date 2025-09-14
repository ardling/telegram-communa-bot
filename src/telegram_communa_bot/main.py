#!/bin/env/python3
from .logging_setup import setup_logging

logger = setup_logging(__file__)

import asyncio
from .bot.bot import run_bot
from .settings import settings


def main():
    logger.info("Start Telegram Lobby Bot...")

    _ = asyncio.run(run_bot(settings()))
