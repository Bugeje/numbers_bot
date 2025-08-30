# helpers/async_util.py
import asyncio
from collections.abc import Callable
from typing import Any

from .concurrency import get_concurrency_manager


async def run_blocking(func: Callable[..., Any], *args, **kwargs) -> Any:
    """
    Выполнит func в отдельном потоке с контролем PDF генерации,
    не блокируя основной цикл бота.
    """
    # Если это PDF генерация, используем семафор
    if 'pdf' in func.__name__.lower() or 'generate' in func.__name__.lower():
        concurrency_manager = get_concurrency_manager()
        async with concurrency_manager.pdf_generation_context():
            return await asyncio.to_thread(func, *args, **kwargs)
    else:
        # Для других операций используем обычный способ
        return await asyncio.to_thread(func, *args, **kwargs)
