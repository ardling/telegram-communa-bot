from enum import Enum

from aiogram import F
from aiogram.types import (
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
async def handle_callback_name(callback: CallbackQuery):
    data = app_data()

    logger.info(f"Update chat_id from {data.chat_id} to {data.new_chat_id}")

    if data.new_chat_id:
        data.chat_id = data.new_chat_id
        data.new_chat_id = None
        data.save()

        _ = await callback.answer(f"Лобби чат теперь {data.chat_id}")
        _ = await bot.send_message(
            data.chat_id, f"Чат зарегистрирован в качестве лобби"
        )

    return await callback.answer(f"Лобби чат не обновлен")
