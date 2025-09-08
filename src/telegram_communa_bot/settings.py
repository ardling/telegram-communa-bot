from pathlib import Path

import os

from .logging_setup import setup_logging


logger = setup_logging(__file__)


def get_env_var(name: str, default: str | None = None) -> str:
    value: str | None = os.getenv(name) or default
    if not value:
        logger.error(f"Enivironment vaiable {name} is not set")
        raise RuntimeError(1)
    return value


def get_token() -> str:
    return get_env_var("TELEGRAM_BOT_TOKEN")


def get_data_path() -> Path:
    return Path(get_env_var("BOT_DATA_PATH", "./data"))
