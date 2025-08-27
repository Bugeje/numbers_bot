# utils/progress.py
import asyncio
from collections.abc import Iterable

from telegram import Chat, Message, Update
from telegram.constants import ChatAction

from .messages import M

# Одно сообщение на этап (без шкал)
PRESETS = {
    "calc_core": [M.PROGRESS.CALC_LABEL],
    "ai": [M.PROGRESS.AI_LABEL],
    "pdf": [M.PROGRESS.PDF_ONE],
    "sending": [M.PROGRESS.SENDING_ONE],
}


class MessageManager:
    """Manages auto-deletion of instruction and navigation messages."""
    
    def __init__(self, context):
        self.context = context
        if "auto_delete_messages" not in context.user_data:
            context.user_data["auto_delete_messages"] = []
    
    def track_message(self, message: Message) -> None:
        """Track a message for auto-deletion."""
        self.context.user_data["auto_delete_messages"].append(message.message_id)
    
    async def cleanup_tracked_messages(self) -> None:
        """Delete all tracked messages."""
        message_ids = self.context.user_data.get("auto_delete_messages", [])
        for msg_id in message_ids:
            try:
                await self.context.bot.delete_message(
                    chat_id=self.context._chat_id, 
                    message_id=msg_id
                )
            except Exception:
                pass  # Message might already be deleted
        
        # Clear the tracking list
        self.context.user_data["auto_delete_messages"] = []
    
    async def send_and_track(self, update: Update, text: str, **kwargs) -> Message:
        """Send a message and automatically track it for deletion."""
        msg = await update.effective_message.reply_text(text, **kwargs)
        self.track_message(msg)
        return msg


async def action_typing(chat: Chat) -> None:
    try:
        await chat.send_action(ChatAction.TYPING)
    except Exception:
        pass


async def action_upload(chat: Chat) -> None:
    try:
        await chat.send_action(ChatAction.UPLOAD_DOCUMENT)
    except Exception:
        pass


class Progress:
    def __init__(self, message: Message):
        self.message = message

    @classmethod
    async def start(cls, update: Update, initial_text: str) -> "Progress":
        msg = await update.effective_message.reply_text(initial_text)
        return cls(msg)

    async def set(self, text: str) -> None:
        try:
            await self.message.edit_text(text)
        except Exception:
            pass

    async def animate(self, frames: Iterable[str], delay: float = 0.0) -> None:
        """
        No-op-анимация: просто один раз устанавливаем конечный текст (без циклов).
        """
        last = None
        for last in frames:
            break
        # если frames — список, берём первый элемент; иначе ничего не делаем
        if last:
            await self.set(last)

    async def animate_until(self, coro, frames, delay: float = 0.0, min_loops: int = 0):
        """
        No-op-анимация: ставим статус один раз и ждём результат корутины.
        """
        first = None
        for first in frames:
            break
        if first:
            await self.set(first)
        return await coro  # ждём без дополнительных правок сообщения

    async def finish(
        self, text: str = M.PROGRESS.DONE, delete_after: float | None = 2.0
    ) -> None:
        """Finish progress with success message and auto-delete."""
        try:
            await self.message.edit_text(text)
            if delete_after:
                await asyncio.sleep(delete_after)
                await self.message.delete()
        except Exception:
            pass

    async def fail(self, text: str = M.PROGRESS.FAIL, delete_after: float | None = 3.0) -> None:
        """Finish progress with error message and auto-delete."""
        try:
            await self.message.edit_text(text)
            if delete_after:
                await asyncio.sleep(delete_after)
                await self.message.delete()
        except Exception:
            pass

    async def cleanup(self) -> None:
        """Immediately delete the progress message without showing completion."""
        try:
            await self.message.delete()
        except Exception:
            pass
