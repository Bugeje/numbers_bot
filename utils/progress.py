# utils/progress.py
import asyncio
from typing import Iterable, Optional
from telegram.constants import ChatAction
from telegram import Update, Message, Chat


PRESETS = {
    # короткие ступени «прогресса»
    "calc_core": [
        "⚙️ Считаю ядро личности…",
        "⚙️ Считаю ядро личности… ⏳ [░░░░░]",
        "⚙️ Считаю ядро личности… ⏳ [█░░░░]",
        "⚙️ Считаю ядро личности… ⏳ [██░░░]",
        "⚙️ Считаю ядро личности… ⏳ [███░░]",
    ],
    "ai": [
        "🤖 Генерирую интерпретацию ИИ…",
        "🤖 Генерирую интерпретацию ИИ… ⏳ [░░░░░]",
        "🤖 Генерирую интерпретацию ИИ… ⏳ [█░░░░]",
        "🤖 Генерирую интерпретацию ИИ… ⏳ [██░░░]",
        "🤖 Генерирую интерпретацию ИИ… ⏳ [███░░]",
    ],
    "pdf": ["📝 Формирую PDF-отчёт…"],
    "sending": ["📤 Отправляю отчёт…"],
}


async def action_typing(chat: Chat) -> None:
    """Отправить системный индикатор 'печатает'."""
    try:
        await chat.send_action(ChatAction.TYPING)
    except Exception:
        pass


async def action_upload(chat: Chat) -> None:
    """Отправить системный индикатор 'загрузка документа'."""
    try:
        await chat.send_action(ChatAction.UPLOAD_DOCUMENT)
    except Exception:
        pass


class Progress:
    """Обёртка над сообщением прогресса с удобными методами."""

    def __init__(self, message: Message):
        self.message = message

    @classmethod
    async def start(cls, update: Update, initial_text: str) -> "Progress":
        """Создать/отправить первое сообщение прогресса и вернуть объект Progress."""
        msg = await update.effective_message.reply_text(initial_text)
        return cls(msg)

    async def set(self, text: str) -> None:
        """Заменить текст прогресса."""
        try:
            await self.message.edit_text(text)
        except Exception:
            pass

    async def animate(self, frames: Iterable[str], delay: float = 0.6) -> None:
        """Проиграть набор кадров (псевдо-анимацию) последовательно."""
        for text in frames:
            await self.set(text)
            await asyncio.sleep(delay)

    async def finish(self, text: str = "✅ Отчёт готов!", delete_after: Optional[float] = 1.2) -> None:
        """Завершить прогресс (по желанию удалить сообщение)."""
        try:
            await self.message.edit_text(text)
            if delete_after:
                await asyncio.sleep(delete_after)
                await self.message.delete()
        except Exception:
            pass

    async def fail(self, text: str = "⚠️ Произошла ошибка.") -> None:
        """Показать, что шаг не удался (сообщение остаётся)."""
        try:
            await self.message.edit_text(text)
        except Exception:
            pass
