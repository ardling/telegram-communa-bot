from telegram_communa_bot.bot.common import lobby_send_message
from ..logging_setup import setup_logging

logger = setup_logging(__file__)

from typing import override
from aiogram import Router
from aiogram.filters import BaseFilter, Command
from aiogram.types import Message

from telegram_communa_bot.bot.app_data import AppData
from telegram_communa_bot.bot.globals import GlobalData


class _AdminFilter(BaseFilter):
    @override
    async def __call__(self, message: Message) -> bool:
        ad: GlobalData = GlobalData.get()
        logger.info(
            "router_admin: message.chat.id=%s, app_data.admin_id=%s",
            message.chat.id,
            ad.admin_id,
        )
        return message.chat.id == ad.admin_id


router_admin = Router(name="admin")


_ = router_admin.message.filter(_AdminFilter())


@router_admin.message(Command("help"))
async def cmd_help(msg: Message):
    return await msg.answer(
        """Команды админа
        - /status
        - /forget
        - /lobby <chat_id> - set lobby chat
        """
    )


@router_admin.message(Command("lobby"))
async def cmd_lobby(msg: Message):
    chat_id = None
    try:
        if not msg.text:
            raise ValueError
        _, chat_id = msg.text.split(" ")
        chat_id = int(chat_id)
    except ValueError:
        if not chat_id:
            return await msg.answer("Использование: /lobby <chat_id>")
        return await msg.answer(f"Неверный chat_id: {chat_id}")

    ad: AppData = AppData.get()
    ad.chat_id = chat_id
    ad.save()

    _ = await msg.answer(f"Новый лобби чат: {chat_id}")
    _ = await lobby_send_message("Част устновлен в качестве lobby")


@router_admin.message(Command("status"))
async def cmd_status(msg: Message):
    return await msg.answer("""TODO""")


@router_admin.message(Command("forget"))
async def cmd_forget(msg: Message):
    return await msg.answer("""TODO""")
