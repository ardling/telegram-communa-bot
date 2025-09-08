from aiogram import Bot, Dispatcher, Router
from aiogram.types import User, Chat
from dotenv import load_dotenv

from .settings import get_token

_ = load_dotenv()


bot: Bot = Bot(get_token())
dp: Dispatcher = Dispatcher()
router = Router()
_ = dp.include_router(router)


def item_str(item: User | Chat | None):
    """Print item readable info"""

    if isinstance(item, User):
        return f"<User: {item.id}, {item.username}, {item.full_name}>"
    if isinstance(item, Chat):
        return f"<Chat: {item.id}, {item.type}, {item.title}>"
    else:
        return f"<Unnown type: {type(item)}>"
