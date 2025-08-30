# helpers/async_util.py
import asyncio
from collections.abc import Callable
from typing import Any

from .concurrency import get_concurrency_manager


async def run_blocking(func: Callable[..., Any], *args, **kwargs) -> Any:
    """
    Выполнит func в отдельном потоке,
    не блокируя основной цикл бота.
    """
    # Для всех операций используем обычный способ
    # PDF generation now uses the PDF queue system instead of semaphores
    return await asyncio.to_thread(func, *args, **kwargs)
