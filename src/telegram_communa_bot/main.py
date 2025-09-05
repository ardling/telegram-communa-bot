#!/bin/env/python3
"""
Telegram Communa Bot - A bot for managing communas in Telegram.
"""

import asyncio
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message


def get_token():
    """Get Telegram bot token from environment variable.

    Returns:
        str: The bot token from TELEGRAM_BOT_TOKEN environment variable.

    Raises:
        SystemExit: If the token is not found in environment variables.
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print(
            "Ошибка: Не указан токен Telegram-бота!\n"
            "Установите переменную окружения TELEGRAM_BOT_TOKEN или передайте токен как аргумент."
        )
        sys.exit(1)
    return token


bot = Bot(get_token())
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Handle /start command - greet the user."""
    return await message.answer("Привет! Я бот коммуны.")


@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command - show available commands."""
    return await message.answer(
        "Я бот для управления коммунами в Telegram. Доступные команды: /start /help"
    )


@dp.message()
async def echo(message: Message):
    """Echo any message back to the user."""
    return await message.answer(f"Вы сказали: {message.text}")


def main():
    """Main function to start the bot polling."""
    asyncio.run(dp.start_polling(bot))


if __name__ == "__main__":
    main()
