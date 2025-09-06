import asyncio
import logging
import secrets
import string
from dataclasses import dataclass
from typing import Dict, Optional

from aiogram import Router, F
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest

logger = logging.getLogger(__name__)

UID_TAG_PREFIX = "[UID:"  
UID_TAG_PATTERN = "[UID:{uid}]"

# Разрешённые типы сообщений (иначе отклоняем в личке, чтобы гарантировать место для UID)
CAPTIONABLE_OR_TEXT = {
    "text",
    "photo",
    "video",
    "animation",
    "document",
}

@dataclass
class ForwardRecord:
    uid: str
    user_id: int
    # id пересланного в группу сообщения (для отладки; сейчас не используется обратным путём)
    group_message_id: Optional[int] = None


class ForwardIndex:
    """
    Память в процессе: UID -> ForwardRecord.
    При рестарте очищается (приемлемо для первой версии).
    """

    def __init__(self):
        self._by_uid: Dict[str, ForwardRecord] = {}

    def put(self, rec: ForwardRecord):
        self._by_uid[rec.uid] = rec

    def get(self, uid: str) -> Optional[ForwardRecord]:
        return self._by_uid.get(uid)


_index = ForwardIndex()


def _generate_uid(length: int = 8) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def extract_uid_from_text(text: str) -> Optional[str]:
    """
    Ищет финальный маркер [UID:XXXX] в тексте/подписи (простая евристика: последний токен вида [UID:...]).
    """
    if not text:
        return None
    # Быстрый путь: ищем предпоследнее вхождение '['
    # Но проще — пробежать по словам в обратном порядке
    for token in reversed(text.strip().split()):
        if token.startswith(UID_TAG_PREFIX) and token.endswith("]"):
            inner = token[len(UID_TAG_PREFIX):-1]  # между префиксом и финальной ]
            if 4 <= len(inner) <= 32 and all(ch in (string.ascii_uppercase + string.digits) for ch in inner):
                return inner
    return None


def setup_forwarding(target_chat_id: int) -> Router:
    """
    Создаёт Router с двумя основными группами хендлеров:
    1. Личные сообщения -> пересылка в целевой чат с добавлением UID
    2. Ответы в целевом чате на сообщения бота -> доставка назад пользователю
    """
    router = Router(name="forwarding")

    @router.message(F.chat.type == "private")
    async def on_private_message(message: Message):
        ctype = message.content_type
        if ctype not in CAPTIONABLE_OR_TEXT:
            await message.answer(
                "Этот тип сообщения пока не поддерживается для пересылки. "
                "Отправьте текст, фото, видео, анимацию или документ."
            )
            return

        uid = _generate_uid()
        rec = ForwardRecord(uid=uid, user_id=message.from_user.id)
        _index.put(rec)

        uid_tag = UID_TAG_PATTERN.format(uid=uid)

        try:
            if ctype == "text":
                # Добавляем UID отдельной строкой
                text = f"{message.text.strip()}\n{uid_tag}"
                sent = await message.bot.send_message(
                    chat_id=target_chat_id,
                    text=text
                )
            else:
                caption_parts = []
                if message.caption:
                    caption_parts.append(message.caption.strip())
                caption_parts.append(uid_tag)
                caption = "\n".join(caption_parts)

                if ctype == "photo":
                    sent = await message.bot.send_photo(
                        chat_id=target_chat_id,
                        photo=message.photo[-1].file_id,
                        caption=caption
                    )
                elif ctype == "video":
                    sent = await message.bot.send_video(
                        chat_id=target_chat_id,
                        video=message.video.file_id,
                        caption=caption
                    )
                elif ctype == "animation":
                    sent = await message.bot.send_animation(
                        chat_id=target_chat_id,
                        animation=message.animation.file_id,
                        caption=caption
                    )
                elif ctype == "document":
                    sent = await message.bot.send_document(
                        chat_id=target_chat_id,
                        document=message.document.file_id,
                        caption=caption
                    )
                else:
                    await message.answer("Неожиданная ошибка обработки типа сообщения.")
                    return
            rec.group_message_id = sent.message_id
            await message.answer("Отправлено в группу.")
        except TelegramBadRequest as e:
            logger.exception("Не удалось переслать сообщение: %s", e)
            await message.answer("Ошибка при пересылке. Сообщите администратору.")
        except Exception:
            logger.exception("Внутренняя ошибка при пересылке")
            await message.answer("Внутренняя ошибка. Попробуйте позже.")

    @router.message(F.chat.id == target_chat_id, F.reply_to_message)
    async def on_group_reply(message: Message):
        # Нужно чтобы родительское сообщение было отправлено ботом и содержало UID
        replied = message.reply_to_message
        if not replied or not replied.from_user or not replied.from_user.is_bot:
            return

        candidate_text = replied.text or replied.caption or ""
        uid = extract_uid_from_text(candidate_text)
        if not uid:
            return

        rec = _index.get(uid)
        if not rec:
            await message.reply("UID не найден (возможно был перезапуск бота).")
            return

        # Формируем ответ для пользователя
        try:
            if message.content_type == "text":
                await message.bot.send_message(
                    chat_id=rec.user_id,
                    text=f"{message.text}"
                )
            elif message.content_type == "photo":
                await message.bot.send_photo(
                    chat_id=rec.user_id,
                    photo=message.photo[-1].file_id,
                    caption=message.caption or ""
                )
            elif message.content_type == "video":
                await message.bot.send_video(
                    chat_id=rec.user_id,
                    video=message.video.file_id,
                    caption=message.caption or ""
                )
            elif message.content_type == "animation":
                await message.bot.send_animation(
                    chat_id=rec.user_id,
                    animation=message.animation.file_id,
                    caption=message.caption or ""
                )
            elif message.content_type == "document":
                await message.bot.send_document(
                    chat_id=rec.user_id,
                    document=message.document.file_id,
                    caption=message.caption or ""
                )
            else:
                await message.reply("Тип ответа не поддерживается для обратной доставки.")
                return

        except TelegramBadRequest as e:
            logger.exception("Не удалось отправить сообщение пользователю: %s", e)
            await message.reply("Не удалось доставить сообщение пользователю.")
        except Exception:
            logger.exception("Неизвестная ошибка при обратной доставке")
            await message.reply("Внутренняя ошибка при обратной доставке.")

    return router