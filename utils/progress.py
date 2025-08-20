# utils/progress.py
import asyncio
from typing import Iterable, Optional
from telegram.constants import ChatAction
from telegram import Update, Message, Chat
from .messages import M


PRESETS = {
    "calc_core": M.PROGRESS.CALC_FRAMES,
    "ai": M.PROGRESS.AI_FRAMES,
    "pdf": [M.PROGRESS.PDF_ONE],
    "sending": [M.PROGRESS.SENDING_ONE],
}


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

    async def animate(self, frames: Iterable[str], delay: float = 0.6) -> None:
        for text in frames:
            await self.set(text)
            await asyncio.sleep(delay)

    async def finish(self, text: str = M.PROGRESS.DONE, delete_after: Optional[float] = 1.2) -> None:
        try:
            await self.message.edit_text(text)
            if delete_after:
                await asyncio.sleep(delete_after)
                await self.message.delete()
        except Exception:
            pass

    async def fail(self, text: str = M.PROGRESS.FAIL) -> None:
        try:
            await self.message.edit_text(text)
        except Exception:
            pass
