# helpers/async_util.py
import asyncio
from collections.abc import Callable
from typing import Any


async def run_blocking(func: Callable[..., Any], *args, **kwargs) -> Any:
    # Выполнит func в отдельном потоке и вернёт результат,
    # не блокируя основной цикл бота (aiogram).
    return await asyncio.to_thread(func, *args, **kwargs)
