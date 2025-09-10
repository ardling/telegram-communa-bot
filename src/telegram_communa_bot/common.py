from aiogram import Bot
from aiogram.types import ReplyMarkupUnion, User, Chat, Message
from .persistent import app_data


def item_str(item: User | Chat | Message | None):
    """Print item readable info"""

    if isinstance(item, User):
        return f"<User: `{item.id}`, @{item.username}, {item.full_name}>"
    if isinstance(item, Chat):
        return f"<Chat: {item.id}, {item.type}, {item.title}>"
    if isinstance(item, Message):
        return f"<Message {item_str(item.chat)} {item_str(item.from_user)}>"
    else:
        return f"<Unnown type: {type(item)}>"


async def user_from_id(id: int) -> User | None:
    try:
        chat = await GlobalBot.get().get_chat(id)
        return User(
            id=chat.id,
            is_bot=False,
            first_name=chat.first_name or "",
            last_name=chat.last_name or "",
            full_name=chat.full_name,
            username=chat.username,
        )
    except ValueError:
        return None


_global_bot: Bot | None = None


class GlobalBot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        global _global_bot
        _global_bot = self

    @staticmethod
    def get() -> Bot:
        if not _global_bot:
            raise SystemExit(1)

        return _global_bot


async def lobby_send_message(text: str, reply_markup: ReplyMarkupUnion | None = None):
    if not _global_bot:
        return SystemExit(1)
    return await _global_bot.send_message(
        app_data().chat_id, text, reply_markup=reply_markup
    )
