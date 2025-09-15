from ..logging_setup import setup_logging

logger = setup_logging(__file__)

from typing import override
from aiogram import Router
from aiogram.filters import BaseFilter, Command
from aiogram.types import Message

from telegram_communa_bot.bot.app_data import app_data, AppData


class _AdminFilter(BaseFilter):
    def __init__(self):
        self._ad: AppData = app_data()

    @override
    async def __call__(self, message: Message) -> bool:
        logger.info(
            "message.chat.id=%s, app_data.admin_id=%s",
            message.chat.id,
            self._ad.admin_id,
        )
        return message.chat.id == self._ad.admin_id


router_admin = Router(name="admin")


_ = router_admin.message.filter(_AdminFilter())


@router_admin.message(Command("/help"))
async def cmd_help(msg: Message):
    return await msg.answer(
        """Команды админа
        - /status
        - /forget
        """
    )


@router_admin.message(Command("status"))
async def cmd_status(msg: Message):
    return await msg.answer("""TODO""")


@router_admin.message(Command("forget"))
async def cmd_forget(msg: Message):
    return await msg.answer("""TODO""")
