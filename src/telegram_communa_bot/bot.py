from .logging_setup import setup_logging

logger = setup_logging(__file__)

from aiogram import Dispatcher, Router, F
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from .settings import get_token
from .persistent import app_data
from .common import GlobalBot, item_str
from .lobby_chat import router_lobby
from .private import router_private
from .public_chat import router_public_chat

router = Router(name="default")


@router.message()
async def fallback(message: Message):
    logger.error(f"Unhandled message '{message.text}',\n{item_str(message)}")
    return await message.answer("Unhandled message")


async def run_bot():
    defaults = DefaultBotProperties(
        parse_mode=ParseMode.MARKDOWN_V2,
        # disable_web_page_preview=True,
        protect_content=False,
    )

    bot = GlobalBot(get_token(), defaults=defaults)
    dp: Dispatcher = Dispatcher()

    logger.info("AppData: %s", app_data())

    _ = dp.include_router(router_lobby)
    _ = dp.include_router(router_private)
    _ = dp.include_router(router_public_chat)
    _ = dp.include_router(router)

    return await dp.start_polling(bot)
