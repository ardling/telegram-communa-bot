from enum import Enum

from aiogram import F
from aiogram.types import (
    User,
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from .logging_setup import setup_logging
from .persistent import app_data
from .bot import bot, router, item_str


logger = setup_logging(__file__)


class IsUpdateChat(Enum):
    yes = "is_update_chat_yes"
    no = "is_update_chat_no"


async def register_lobby_chat(message: Message):
    logger.info("New main chat {}", item_str(message.chat))

    data = app_data()
    if data.chat_id == message.chat.id:
        return await message.answer("Этот чат уже зарегистрирован")

    data = app_data()
    data.new_chat_id = message.chat.id

    ikb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Нет", callback_data=IsUpdateChat.no.value)],
            [InlineKeyboardButton(text="Да", callback_data=IsUpdateChat.yes.value)],
        ]
    )
    _ = await bot.send_message(
        data.chat_id,
        f"""Подтвердите изменения лобби чата, новый чат: {item_str(message.chat)}""",
        reply_markup=ikb,
    )


@router.callback_query(F.data == IsUpdateChat.yes.value)
async def update_chat_yes(callback: CallbackQuery):
    data = app_data()

    logger.info(f"Update chat_id from {data.chat_id} to {data.new_chat_id}")

    _ = await callback.message.edit_reply_markup(reply_markup=None)

    if not data.new_chat_id:
        return await callback.answer(f"Лобби чат не обновлен")

    old_chat = data.chat_id
    data.chat_id = data.new_chat_id
    data.new_chat_id = None
    data.save()

    _ = await bot.send_message(
        old_chat,
        f"""
        Пользователь {item_str(callback.from_user)} подтвердил, что лобби теперь {data.chat_id}.""",
    )
    _ = await bot.send_message(data.chat_id, f"Чат зарегистрирован в качестве лобби")


@router.callback_query(F.data == IsUpdateChat.no.value)
async def update_chat_no(callback: CallbackQuery):
    data = app_data()
    user: User = callback.from_user

    logger.info(
        f"Rejected update chat_id from {data.chat_id} to {data.new_chat_id} by user {item_str(user)}"
    )

    _ = await callback.message.edit_reply_markup(reply_markup=None)
    _ = await bot.send_message(
        data.chat_id,
        f"""Переносс лобби в что {data.chat_id} отклонен пользователем {item_str(user)}.""",
    )
