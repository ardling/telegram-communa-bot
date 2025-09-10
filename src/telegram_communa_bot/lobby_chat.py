from .logging_setup import setup_logging

logger = setup_logging(__file__)

import asyncio
import re
from typing import override
from collections.abc import Iterable  # , Awaitable, Callable

from aiogram import Router, F
from aiogram.filters import BaseFilter

# from aiogram.dispatcher.event.handler import CallbackType
from aiogram.types import (
    User,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from aiogram.filters import Command

from .common import GlobalBot, item_str, user_from_id, lobby_send_message
from .persistent import AppData, app_data, users_lists

PREFIX_PATTERN = re.compile(r"^\[(\d+)\s@")


class LobbyFilter(BaseFilter):
    def __init__(self):
        self._ad: AppData = app_data()

    @override
    async def __call__(self, message: Message) -> bool:
        logger.info(
            "message.chat.id=%s, app_data.chat_id=%s",
            message.chat.id,
            self._ad.chat_id,
        )
        return message.chat.id == self._ad.chat_id


router_lobby = Router(name="lobby")

_lobby_filter = LobbyFilter()
_ = router_lobby.message.filter(_lobby_filter)

router_questsions = Router(name="questons")
_ = router_lobby.include_router(router_questsions)


@router_lobby.message(F.reply_to_message != None)
async def reply(message: Message):
    """Handle replies in the group and forward back to original user."""
    user_id = message.reply_to_message.forward_from.id

    if not user_id:
        return await message.answer("Невозможно ответить отправителю")

    return await message.forward(user_id)


def dot_list(lst: Iterable[User]) -> str:
    out_lst = [" "]
    out_lst.extend(item_str(i) for i in lst)
    return "\n - ".join(out_lst).strip()


@router_lobby.message(Command("start"))
async def lobby_start(message: Message):
    logger.info("Start command in lobby, %s", item_str(message.chat))

    data = app_data()
    if data.chat_id == message.chat.id:
        return await message.answer(
            """Этот чат уже зарегистрирован в качестве лобби. 
               Команда /help покажет справку"""
        )


@router_lobby.message(Command("whitelist"))
async def cmd_whitelist(message: Message):
    lst = await asyncio.gather(*(user_from_id(x) for x in users_lists().white_list))
    users = filter(None, lst)
    return await message.answer("Пользователи в белом спске:\n" + dot_list(users))


@router_lobby.message(Command("blacklist"))
async def cmd_blacklist(message: Message):
    lst = await asyncio.gather(*(user_from_id(x) for x in users_lists().black_list))
    users = filter(None, lst)
    return await message.answer("Пользователи в черном спске:\n" + dot_list(users))


@router_lobby.message(Command("waitlist"))
async def cmd_waitlist(message: Message):
    lst = await asyncio.gather(*(user_from_id(x) for x in users_lists().wait_list))
    users = filter(None, lst)
    return await message.answer("Пользователи в листе ожидания:\n" + dot_list(users))


async def user_from_message_1(message: Message) -> User | None:
    if not message.text:
        _ = await message.answer("Укажите идентификатор пользователя")
        return None

    try:
        user_id = int(message.text.split(" ")[1].strip())
    except IndexError:
        _ = await message.answer("Укажите идентификатор пользователя")
    except ValueError:
        _ = await message.answer(f"Неправильный идентификатор пользователя")
    else:
        return await user_from_id(user_id)


@router_lobby.message(Command("allow"))
async def cmd_allow(message: Message):
    user = await user_from_message_1(message)
    if not user:
        return None

    ul = users_lists()

    if user.id in ul.white_list:
        return await message.answer(
            f"Пользователь {item_str(user)} уже был одобрен ранее"
        )

    ul.white_list.add(user.id)
    if user.id in ul.wait_list:
        ul.wait_list.remove(user.id)
        ul.save()
        return await message.answer(f"Пользователь {item_str(user)} одобрен")
    if user.id in ul.black_list:
        ul.black_list.remove(user.id)
        ul.save()
        return await message.answer(f"Пользователь {item_str(user)} одобрен")

    return await message.answer(f"Неизвестный пользователь {item_str(user)}")


@router_lobby.message(Command("block"))
async def cmd_block(message: Message):
    user = await user_from_message_1(message)
    if not user:
        return None

    ul = users_lists()
    ul.white_list.discard(user.id)
    ul.wait_list.discard(user.id)
    ul.black_list.add(user.id)
    ul.save()

    return await message.answer(
        f"Пользователь {item_str(user)} заблокирован. Теперь он не может писать сообщения"
    )


@router_lobby.message(Command("forget"))
async def cmd_forget(message: Message):
    user = await user_from_message_1(message)
    if not user:
        return None

    ul = users_lists()
    ul.wait_list.discard(user.id)
    ul.white_list.discard(user.id)
    ul.black_list.discard(user.id)
    ul.save()

    return await message.answer("Пользователь удален из всех списков")


@router_lobby.message(Command("help"))
async def cmd_help(message: Message):
    return await message.answer(
        """
      Этот бот пересылает отправленные ему сообщения в чат Лобби (сюда).
      Чтобы начать работы с ботом напишите ему /start.

      Доступные команды: 
      - /start - начать работу с ботом
      - /help  - это сообщение :)

      - /whitelist - посмотреть список пользователей которые вам писать
      - /waitlist - увидеть пользователей в листе ождания
      - /blacklist - заблокированные пользователи

      - /allow <user_id> - разрешить полльзвателю послылать сообщения
      - /block <user_id> - заблокировать пользователя

      `user_id` - это первая цифра в списках пользователей
    """
    )


# HandlerType = Awaitable[Message]


# def callback_data(tag: str, data: str, value: str = "") -> str:
#     return f"{tag}:{data}:{value}"
#
#
# def _handler_wrapper(func: Callable[[str, str], None]):
#     async def tmp(full_data: str) -> Callable[[str], None]:
#         _, data, answer = full_data.split(":")
#         return func(data, answer)
#
#     return tmp
#
#
# async def lobby_question_about_user(
#     handler: CallbackType,
#     question: str,
#     answers: dict[str, str],
#     data: str,
#     tag: str | None = None,
# ):
#     tag = tag or handler.__name__
#
#     kb = InlineKeyboardMarkup(
#         inline_keyboard=[
#             [
#                 InlineKeyboardButton(
#                     text=k,
#                     callback_data=callback_data(tag, data, v),
#                 )
#                 for k, v in answers
#             ]
#         ]
#     )
#
#     # register question handler
#     _ = router_lobby.message(F.data.startswith(callback_data(tag, data)))(
#         _handler_wrapper(handler)
#     )
#
#     return await lobby_send_message(question, reply_markup=kb)


ASK_ALLOW = "allow_user"


async def ask_allow_user(user: User):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Нет", callback_data=f"{ASK_ALLOW}:{user.id}:no"
                ),
                InlineKeyboardButton(
                    text="Да", callback_data=f"{ASK_ALLOW}:{user.id}:yes"
                ),
            ]
        ]
    )
    return await lobby_send_message(
        f"Пользователь {item_str(user)} хочет писать сообщения, разрешить?",
        reply_markup=kb,
    )


@router_questsions.callback_query(F.data.startswith(f"{ASK_ALLOW}:"))
async def handle_answer(query: CallbackQuery):
    _ = await query.answer()
    _, user_id, choice = query.data.split(":", 2)
    user_id = int(user_id)

    ul = users_lists()
    bot = GlobalBot.get()

    if choice == "yes":
        ul.white_list.add(user_id)
        _ = await bot.send_message(user_id, "Доступ разрешен")
    else:
        ul.black_list.add(user_id)
        _ = await bot.send_message(user_id, "Доступ запрещен")

    ul.wait_list.discard(user_id)
    ul.save()

    _ = await query.message.edit_reply_markup(reply_markup=None)
