from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.types import Message
from aiogram.filters import Command

from ..logging_setup import setup_logging
from .app_data import app_data, users_lists
from .common import item_str
from .lobby_chat import ask_allow_user

logger = setup_logging(__file__)


router_private = Router(name="provate")
router_private.message.filter(F.chat.type == ChatType.PRIVATE)


@router_private.message(Command("start"))
async def cmd_start(message: Message):
    logger.info("/start in with chat_id: %s", item_str(message.chat))

    ul = users_lists()

    if not message.from_user:
        logger.warning("Unnown user try to register")
        return None

    user = message.from_user
    if user.id in ul.white_list:
        return await message.answer("Отправь сообщение и я перешлю его в лобби чат")

    if user.id in ul.black_list:
        return await message.answer("Бот не будет передавать твои сообщения")

    ul.wait_list.add(user.id)
    ul.save()

    _ = await ask_allow_user(user)
    return await message.answer("Привет, ты добавлен в лист ожидания")


@router_private.message()
async def handle_message(message: Message):
    """Main message handler for private chats."""
    white_list = users_lists().white_list
    if not message.from_user or message.from_user.id not in white_list:
        return await message.answer("Тебя нет в списке допущенных пользователей")

    ad = app_data()
    return await message.forward(ad.chat_id)
