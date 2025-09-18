"""
All public chats not registered as lobby considering as
potential new lobby chats.
"""

from ..logging_setup import setup_logging

logger = setup_logging(__file__)

from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.types import Message
from aiogram.filters import Command


from .app_data import AppData


router_public_chat = Router(name="public_chat")
router_public_chat.message.filter(
    F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP})
)


@router_public_chat.message(Command("start"))
async def cmd_start(message: Message):
    data = AppData.get()
    data.new_chat_id = message.chat.id

    _ = await message.answer(
        f"""
        ID чата: `{message.chat.id}`, 
        для назначения в качестве лобби пришлите его админу бота.
        Если хотите оправить сообщение, пишите боту в личку""",
    )
