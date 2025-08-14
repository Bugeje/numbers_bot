# utils/async_tools.py
import asyncio
from typing import Any, Callable

async def run_blocking(func: Callable[..., Any], *args, **kwargs) -> Any:
    # Выполнит func в отдельном потоке и вернёт результат,
    # не блокируя основной цикл бота (aiogram).
    return await asyncio.to_thread(func, *args, **kwargs)
