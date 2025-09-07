#!/bin/env/python3

import asyncio
import sys
import json
import re
from aiogram import Bot, Dispatcher
from aiogram.types import Message, User
from aiogram.filters import Command
from dotenv import load_dotenv
from pathlib import Path
from pydantic import BaseModel

import os

from .logging_setup import setup_logging

logger = setup_logging(__file__)

uid_mapping: dict[str, int] = {}
user_uid_mapping: dict[int, str] = {}

PERSISTENT_FILE_PATH = "persistent.json"
PREFIX_PATTERN = re.compile(r"^\[(\d+)\s@")


def get_data_path() -> Path:
    return Path(get_env_var("BOT_DATA_PATH", "./data"))


class Persistent(BaseModel):
    chat_id: int = 0

    @staticmethod
    def load():
        path: Path = get_data_path().joinpath(PERSISTENT_FILE_PATH)

        logger.info("Load data from path {}", path)

        try:
            return Persistent.model_validate(
                json.loads(path.read_text(encoding="utf-8"))
            )
        except FileNotFoundError:
            data = Persistent()
            data.save()
            return data

    def save(self) -> None:
        path: Path = get_data_path().joinpath(PERSISTENT_FILE_PATH)

        logger.info("Save data from path {}", path)

        _ = path.write_text(self.model_dump_json(indent=2), encoding="utf-8")


__persistent: Persistent | None = None


def persistent() -> Persistent:
    global __persistent
    if not __persistent:
        __persistent = Persistent.load()
    return __persistent


def get_env_var(name: str, default: str | None = None) -> str:
    value: str | None = os.getenv(name) or default
    if not value:
        logger.error(f"Enivironment vaiable {name} is not set")
        sys.exit(1)
    return value


def get_token() -> str:
    return get_env_var("TELEGRAM_BOT_TOKEN")


def get_user_by_uid(uid: str) -> int | None:
    """Get user_id by UID."""
    return uid_mapping.get(uid)


_ = load_dotenv()
bot: Bot = Bot(get_token())
dp: Dispatcher = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: Message):
    chat_id: int = message.chat.id
    if chat_id < 0:
        logger.info("/start in with chat_id: {}", chat_id)
        data = persistent()
        data.chat_id = chat_id
        data.save()

    return await message.answer(
        f"""
        Привет! Я бот коммуны. Я буду пересылвать сообщения в этот чат.

        ===
        chat_id: {message.chat.id}
    """
    )


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
            f"Forwarded message from user {user.id} to group {persistent().chat_id}"
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
        if message.chat.id == persistent().chat_id:
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
        _ = await bot.send_message(persistent().chat_id, f"{prefix} {message.text}")
    elif message.photo:
        # Photo message
        _ = await bot.send_photo(
            persistent().chat_id,
            message.photo[-1].file_id,  # Get highest resolution
            caption=f"{prefix} {message.caption or ''}",
        )
    elif message.video:
        # Video message
        _ = await bot.send_video(
            persistent().chat_id,
            message.video.file_id,
            caption=f"{prefix} {message.caption or ''}",
        )
    elif message.animation:
        # GIF/Animation message
        _ = await bot.send_animation(
            persistent().chat_id,
            message.animation.file_id,
            caption=f"{prefix} {message.caption or ''}",
        )
    elif message.document:
        # Document message
        _ = await bot.send_document(
            persistent().chat_id,
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
