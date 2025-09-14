from .logging_setup import setup_logging

logger = setup_logging(__file__)

import os
from pathlib import Path
from dataclasses import dataclass

from dotenv import load_dotenv


def get_env_var(name: str, default: str | None = None) -> str | None:
    value: str | None = os.getenv(name) or default
    if not value:
        logger.error(f"Enivironment vaiable {name} is not set")
        return None
    return value.strip()


@dataclass(frozen=True)
class Settings:
    token: str
    data_path: Path
    admin: str


__settings: Settings | None = None


def settings() -> Settings:
    global __settings
    if __settings:
        return __settings

    _ = load_dotenv()
    token = get_env_var("TELEGRAM_BOT_TOKEN")
    data_path = Path(get_env_var("BOT_DATA_PATH") or "")
    admin = get_env_var("BOT_ADMIN")

    if not token or not data_path or not admin:
        raise SystemExit(1)

    return Settings(
        token=token,
        data_path=data_path,
        admin=admin,
    )
