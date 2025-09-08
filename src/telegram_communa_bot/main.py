#!/bin/env/python3

import asyncio
import re
from aiogram.types import (
    Message,
    User,
    Chat,
)
from aiogram.filters import Command

from telegram_communa_bot.persistent import app_data

from .logging_setup import setup_logging
from .bot import bot, dp, item_str
from .lobby_chat import register_lobby_chat

logger = setup_logging(__file__)

uid_mapping: dict[str, int] = {}
user_uid_mapping: dict[int, str] = {}

PREFIX_PATTERN = re.compile(r"^\[(\d+)\s@")


async def register_user(message: Message):
    return await message.answer(
        f"""
        Привет, ты добавлен в лист ожидания"""
    )


@dp.message(Command("start"))
async def cmd_start(message: Message):
    chat: Chat = message.chat
    logger.info("/start in with chat_id: {}", item_str(chat))

    # chat ID is lower then 0
    if chat.id < 0:
        _ = await register_lobby_chat(message)
    else:
        _ = await register_user(message)


@dp.message(Command("help"))
async def cmd_help(message: Message):
    return await message.answer(
        """
      Доступные команды: 
      - /start 
      - /help
    """
    )


async def forward_to_group(message: Message) -> None:
    """Forward message from private chat to target group."""
    user: User | None = message.from_user
    if not user:
        logger.error("Answer in group without 'from_user' field")
        return None
    try:
        prefix = f"""[{user.id} @{' '.join([
            (user.username or ''),
            (user.first_name or ''),
            (user.last_name or '')
        ]).strip()}]: """
        await forward_message(message, prefix)

        logger.info(
            f"Forwarded message from user {user.id} to group {app_data().chat_id}"
        )
        _ = await message.answer("Сообщение отправлено в группу.")

    except Exception as e:
        logger.error(f"Failed to forward message from user {user.id}: {e}")
        _ = await message.answer("Произошла ошибка при отправке сообщения.")


async def handle_group_reply(message: Message):
    """Handle replies in the group and forward back to original user."""
    if (
        not message.reply_to_message
        or not message.reply_to_message.from_user
        or not message.from_user
    ):
        logger.error("Message without reply or from_user")
        return None

    # Check if the replied message is from our bot
    if message.reply_to_message.from_user.id != bot.id:
        return None

    user: User = message.from_user

    original_text = (
        message.reply_to_message.text or message.reply_to_message.caption or ""
    )

    match = PREFIX_PATTERN.match(original_text)
    if not match:
        logger.warning(f"Unknown UID in reply: {original_text}")
        return None

    user_id: str = match.group(1)

    try:
        _ = await bot.send_message(
            user_id,
            f"Ответ из группы: [@{user.username} {' '.join([
                user.first_name or '',
                user.last_name or '',
            ]).strip()}]: {message.text or '[медиа-файл]'}",
        )
        logger.info(f"Forwarded reply from group to user {user_id})")
    except Exception as e:
        logger.error(f"Failed to handle group reply: {e}")


@dp.message()
async def handle_message(message: Message):
    """Main message handler for both private chats and group messages."""
    try:
        if message.chat.id == app_data().chat_id:
            await handle_group_reply(message)
            return

        if message.chat.type == "private":
            # Skip commands
            if message.text and message.text.startswith("/"):
                return

            await forward_to_group(message)
            return
    except Exception as e:
        logger.error(f"Error in message handler: {e}")
        if message.chat.type == "private":
            _ = await message.answer("Произошла ошибка при обработке сообщения.")


async def forward_message(message: Message, prefix: str):
    if message.text:
        # Text message
        _ = await bot.send_message(app_data().chat_id, f"{prefix} {message.text}")
    elif message.photo:
        # Photo message
        _ = await bot.send_photo(
            app_data().chat_id,
            message.photo[-1].file_id,  # Get highest resolution
            caption=f"{prefix} {message.caption or ''}",
        )
    elif message.video:
        # Video message
        _ = await bot.send_video(
            app_data().chat_id,
            message.video.file_id,
            caption=f"{prefix} {message.caption or ''}",
        )
    elif message.animation:
        # GIF/Animation message
        _ = await bot.send_animation(
            app_data().chat_id,
            message.animation.file_id,
            caption=f"{prefix} {message.caption or ''}",
        )
    elif message.document:
        # Document message
        _ = await bot.send_document(
            app_data().chat_id,
            message.document.file_id,
            caption=f"{prefix} {message.caption or ''}",
        )
    else:
        # Unsupported message type
        _ = await message.answer("Извините, этот тип сообщения не поддерживается.")
        return


def main():
    logger.info("Start Telegram Communa Bot...")
    asyncio.run(dp.start_polling(bot))
