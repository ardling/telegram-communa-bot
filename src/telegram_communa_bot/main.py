# Original content of the file with an added empty line
import asyncio
import sys
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from dotenv import load_dotenv

import os
from .logging_setup import setup_logging

logger = setup_logging(__file__)

def get_token():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("env var TELEGRAM_BOT_TOKEN is not set")
        sys.exit(1)
    return token

_ = load_dotenv()
bot = Bot(get_token())
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    return await message.answer("Привет! Я бот коммуны.")

@dp.message(Command("help"))
async def cmd_help(message: Message):
    return await message.answer("Я бот для управления коммунами в Telegram. Доступные команды: /start /help")

@dp.message()
async def echo(message: Message):
    return await message.answer(f"Вы сказали: {message.text}")

def main():
    logger.info("Запуск Telegram Communa Bot...")
    asyncio.run(dp.start_polling(bot))

if __name__ == "__main__":
    main()
