#!/bin/env/python3

import asyncio
import sys
import uuid
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from dotenv import load_dotenv

import os

from .logging_setup import setup_logging

logger = setup_logging(__file__)

uid_mapping: dict[str, int] = {}
user_uid_mapping: dict[int, str] = {}

def get_token():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("env var TELEGRAM_BOT_TOKEN is not set")
        sys.exit(1)
    return token

def get_target_group_id():
    group_id = os.getenv("TARGET_GROUP_ID")
    if not group_id:
        logger.error("env var TARGET_GROUP_ID is not set")
        sys.exit(1)
    try:
        return int(group_id)
    except ValueError:
        logger.error("TARGET_GROUP_ID must be a valid integer")
        sys.exit(1)

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
TARGET_GROUP_ID = get_target_group_id()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    return await message.answer("Привет! Я бот коммуны. Отправьте мне сообщение, и я перешлю его в группу.")

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
            
        logger.info(f"Forwarded message from user {user_id} (UID: {uid}) to group {TARGET_GROUP_ID}")
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
        if message.chat.id == TARGET_GROUP_ID:
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
            TARGET_GROUP_ID,
            f"{prefix} {message.text}"
        )
    elif message.photo:
        # Photo message
        _ = await bot.send_photo(
            TARGET_GROUP_ID,
            message.photo[-1].file_id,  # Get highest resolution
            caption=f"{prefix} {message.caption or ''}"
        )
    elif message.video:
        # Video message
        _ = await bot.send_video(
            TARGET_GROUP_ID,
            message.video.file_id,
            caption=f"{prefix} {message.caption or ''}"
        )
    elif message.animation:
        # GIF/Animation message
        _ = await bot.send_animation(
            TARGET_GROUP_ID,
            message.animation.file_id,
            caption=f"{prefix} {message.caption or ''}"
        )
    elif message.document:
        # Document message
        _ = await bot.send_document(
            TARGET_GROUP_ID,
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

