#!/bin/env/python3

import asyncio
import sys
import uuid
import json
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from dotenv import load_dotenv
from pathlib import Path
from typing import Any
from pydantic import BaseModel

import os
import os.path

from .logging_setup import setup_logging

logger = setup_logging(__file__)

uid_mapping: dict[str, int] = {}
user_uid_mapping: dict[int, str] = {}

PERSISTENT_FILE_PATH="persistent.json"


def get_data_path() -> Path:
    return Path(get_env_var("BOT_DATA_PATH", "./data"))


class Persistent(BaseModel):
    chat_id: int | None = None

    @staticmethod
    def load():
        path: Path = get_data_path().joinpath(PERSISTENT_FILE_PATH)

        logger.info("Load data from path {}", path)

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return Persistent.model_validate(data)
        except FileNotFoundError:
            data = Persistent()
            data.save()
            return data


    def save(self) -> None:
        path: Path = get_data_path().joinpath(PERSISTENT_FILE_PATH)

        logger.info("Save data from path {}", path)

        _ = path.write_text(
            self.model_dump_json(indent=2),
            encoding="utf-8"
        )


__persistent: Persistent | None = None


def persistent() -> Persistent:
    global __persistent
    if not __persistent:
        __persistent = Persistent.load()
    return __persistent


def get_env_var(name: str, default: str | None=None) -> str:
    value: str | None = os.getenv(name) or default
    if not value:
        logger.error(f"Enivironment vaiable {name} is not set")
        sys.exit(1)
    return value



def get_token() -> str:
    return get_env_var("TELEGRAM_BOT_TOKEN")


def generate_uid(user_id: int) -> str:
    """Generate or retrieve UID for a user."""
    if user_id in user_uid_mapping:
        return user_uid_mapping[user_id]
    
    uid = str(uuid.uuid4())[:8].upper()
    uid_mapping[uid] = user_id
    user_uid_mapping[user_id] = uid
    logger.info(f"Generated new UID {uid} for user {user_id}")
    return uid

def get_user_by_uid(uid: str) -> int | None:
    """Get user_id by UID."""
    return uid_mapping.get(uid)

_ = load_dotenv()
bot = Bot(get_token())
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: Message):
    chat_id: int = message.chat.id
    if chat_id < 0:
        data = persistent()
        data.chat_id = chat_id
        data.save()

    return await message.answer(f"""
        Привет! Я бот коммуны. Отправьте мне сообщение, и я перешлю его в группу.

        ===
        chat_id: {message.chat.id}
    """)

@dp.message(Command("help"))
async def cmd_help(message: Message):
    return await message.answer("""
      Доступные команды: 
      - /start 
      - /help
    """)
  

async def forward_to_group(message: Message, user_id: int, uid: str):
    """Forward message from private chat to target group with UID marker."""
    try:
        prefix = f"[UID:{uid}]"
        await forward_message(message, prefix)
            
        logger.info(f"Forwarded message from user {user_id} (UID: {uid}) to group {persistent().chat_id}")
        _ = await message.answer("Сообщение отправлено в группу.")
        
    except Exception as e:
        logger.error(f"Failed to forward message from user {user_id}: {e}")
        _ = await message.answer("Произошла ошибка при отправке сообщения.")

async def handle_group_reply(message: Message):
    """Handle replies in the group and forward back to original user."""
    if not message.reply_to_message:
        return
        
    # Check if the replied message is from our bot
    if message.reply_to_message.from_user.id != bot.id:
        return
        
    # Extract UID from the original message
    original_text = message.reply_to_message.text or message.reply_to_message.caption or ""
    if not original_text.startswith("[UID:"):
        return
        
    try:
        uid_end = original_text.find("]")
        if uid_end == -1:
            return
            
        uid = original_text[5:uid_end]  # Extract UID between [UID: and ]
        user_id = get_user_by_uid(uid)
        
        if not user_id:
            logger.warning(f"Unknown UID in reply: {uid}")
            return
            
        # Forward reply back to the original user
        _ = await bot.send_message(
            user_id,
            f"Ответ из группы: {message.text or '[медиа-файл]'}"
        )
        
        logger.info(f"Forwarded reply from group to user {user_id} (UID: {uid})")
        
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
                
            user_id = message.from_user.id
            uid = generate_uid(user_id)
            await forward_to_group(message, user_id, uid)
            return
    except Exception as e:
        logger.error(f"Error in message handler: {e}")
        if message.chat.type == "private":
            _ = await message.answer("Произошла ошибка при обработке сообщения.")


async def forward_message(message: Message, prefix: str):
    if message.text:
        # Text message
        _ = await bot.send_message(
            persistent().chat_id,
            f"{prefix} {message.text}"
        )
    elif message.photo:
        # Photo message
        _ = await bot.send_photo(
            persistent().chat_id,
            message.photo[-1].file_id,  # Get highest resolution
            caption=f"{prefix} {message.caption or ''}"
        )
    elif message.video:
        # Video message
        _ = await bot.send_video(
            persistent().chat_id,
            message.video.file_id,
            caption=f"{prefix} {message.caption or ''}"
        )
    elif message.animation:
        # GIF/Animation message
        _ = await bot.send_animation(
            persistent().chat_id,
            message.animation.file_id,
            caption=f"{prefix} {message.caption or ''}"
        )
    elif message.document:
        # Document message
        _ = await bot.send_document(
            persistent().chat_id,
            message.document.file_id,
            caption=f"{prefix} {message.caption or ''}"
        )
    else:
        # Unsupported message type
        _ = await message.answer("Извините, этот тип сообщения не поддерживается.")
        return


def main():
    logger.info("Start Telegram Communa Bot...")
    asyncio.run(dp.start_polling(bot))

