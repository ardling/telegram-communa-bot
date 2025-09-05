#!/bin/env/python3

import asyncio
import sys
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

import os

# Получаем токен из переменной окружения или аргумента командной строки
def get_token():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Ошибка: Не указан токен Telegram-бота!\n"
              "Установите переменную окружения TELEGRAM_BOT_TOKEN или передайте токен как аргумент.")
        sys.exit(1)
    return token

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
    asyncio.run(dp.start_polling(bot))

if __name__ == "__main__":
    main()
