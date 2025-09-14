from ..logging_setup import setup_logging

logger = setup_logging(__file__)

from dataclasses import dataclass

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from aiogram.client.default import DefaultBotProperties

from ..settings import Settings


class GlobalBot:
    def __init__(self, token: str, defaults: DefaultBotProperties):
        self._bot: Bot = Bot(token=token, defaults=defaults)
        global _global_bot
        _global_bot = self

    @staticmethod
    def get() -> Bot:
        if not _global_bot:
            raise SystemExit(1)

        return _global_bot._bot


_global_bot: GlobalBot | None = None


@dataclass(frozen=True)
class GlobalData:
    admin_id: int

    @staticmethod
    def get():
        return _global_data

    @staticmethod
    async def init(settings: Settings):
        admin_id = await username_to_id(settings.admin)
        if not admin_id:
            logger.error(f"Incorrect admin: {settings.admin}")
            raise SystemExit(1)

        global _global_data
        _global_data = GlobalData(admin_id=admin_id)


_global_data: GlobalData


async def username_to_id(username: str) -> int | None:

    if not username.startswith("@"):
        username = "@" + username

    logger.info("admin username: %s", username)
    try:
        chat = await GlobalBot.get().get_chat(username)
        return chat.id
    except TelegramForbiddenError:
        # бот заблокирован или нет доступа
        return None
    except TelegramBadRequest as e:
        # например: chat not found
        logger.error("Can't convert username to id: %s", e)
        return None
