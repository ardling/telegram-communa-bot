"""
All public chats not registered as lobby considering as
potential new lobby chats.
"""

from enum import Enum
from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.types import (
    CallbackQuery,
    Message,
    User,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.filters import Command


from .logging_setup import setup_logging
from .common import lobby_send_message, item_str
from .persistent import app_data
from .lobby_chat import router_lobby

logger = setup_logging(__file__)


router_public_chat = Router(name="public_chat")
router_public_chat.message.filter(
    F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP})
)


class IsUpdateChat(Enum):
    yes = "is_update_chat_yes"
    no = "is_update_chat_no"


@router_public_chat.message(Command("start"))
async def cmd_start(message: Message):
    data = app_data()
    data.new_chat_id = message.chat.id

    ikb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Нет", callback_data=IsUpdateChat.no.value)],
            [InlineKeyboardButton(text="Да", callback_data=IsUpdateChat.yes.value)],
        ]
    )
    _ = await lobby_send_message(
        f"""Подтвердите изменения лобби чата, новый чат: {item_str(message.chat)}""",
        reply_markup=ikb,
    )


@router_lobby.callback_query(F.data == IsUpdateChat.yes.value)
async def update_chat_yes(callback: CallbackQuery):
    data = app_data()

    logger.info(f"Update chat_id from {data.chat_id} to {data.new_chat_id}")

    _ = await callback.message.edit_reply_markup(reply_markup=None)

    if not data.new_chat_id:
        return await callback.answer(f"Лобби чат не обновлен")

    _ = await lobby_send_message(
        f"""Пользователь {item_str(callback.from_user)} подтвердил, что лобби теперь {data.chat_id}.""",
    )

    data.chat_id = data.new_chat_id
    data.new_chat_id = None
    data.save()

    _ = await lobby_send_message(
        """Чат зарегистрирован в качестве лобби. Команда /help покажет справку."""
    )


@router_lobby.callback_query(F.data == IsUpdateChat.no.value)
async def update_chat_no(callback: CallbackQuery):
    data = app_data()
    user: User = callback.from_user

    logger.info(
        f"Rejected update chat_id from {data.chat_id} to {data.new_chat_id} by user {item_str(user)}"
    )

    _ = await callback.message.edit_reply_markup(reply_markup=None)
    _ = await lobby_send_message(
        f"""Переносс лобби в чат {data.chat_id} отклонен пользователем {item_str(user)}.""",
    )
