import asyncio
import logging

import httpx

from config import settings
from helpers import M
from helpers.http_pool import get_http_pool

API_URL = f"{settings.ai.openrouter_base_url}/chat/completions"
MODEL = "openai/gpt-4o"
DEBUG = False

logger = logging.getLogger(__name__)


async def ask_openrouter(
    system_prompt: str,
    user_prompt: str,
    *,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> str:
    """Ask OpenRouter API with proper error handling and retries using HTTP client pool."""
    temperature = settings.ai.temperature if temperature is None else temperature
    max_tokens = settings.ai.max_tokens if max_tokens is None else max_tokens
    
    if not settings.ai.openrouter_api_key:
        logger.error("Missing OpenRouter API key")
        return "❌ Ошибка конфигурации: отсутствует API ключ OpenRouter"
    
    # Валидация входных данных
    if not system_prompt or not user_prompt:
        logger.error(f"Invalid prompts: system={bool(system_prompt)}, user={bool(user_prompt)}")
        return "❌ Ошибка: некорректные данные для анализа"

    headers = {
        "Authorization": f"Bearer {settings.ai.openrouter_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_prompt.strip()},
        ],
    }

    # Get HTTP client from pool
    try:
        http_pool = await get_http_pool()
    except Exception as e:
        logger.error(f"Failed to get HTTP client pool: {e}")
        if "h2" in str(e).lower():
            return "❌ Ошибка соединения: HTTP/2 поддержка недоступна. Проверьте установку зависимостей."
        return "❌ Ошибка соединения: не удалось инициализировать HTTP клиент"

    delay = 0.5
    last_error = None
    
    for attempt in range(3):
        try:
            logger.debug(f"AI request attempt {attempt + 1}/3")
            
            async with http_pool.client_context() as client:
                resp = await client.post(API_URL, headers=headers, json=payload)
                
                # Проверяем статус ответа
                if resp.status_code == 200:
                    data = resp.json()

                    if "choices" not in data or not data["choices"]:
                        logger.error(f"Invalid API response structure: {data}")
                        return "❌ Получен некорректный ответ от AI сервиса"

                    content = data["choices"][0]["message"]["content"].strip()
                    
                    if not content:
                        logger.warning("AI returned empty content")
                        return "❌ AI вернул пустой ответ"
                    
                    logger.info(f"AI request successful on attempt {attempt + 1}")
                    return content
                else:
                    # Обрабатываем HTTP ошибки
                    resp.raise_for_status()

        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            last_error = e
            
            logger.warning(f"HTTP error {status} on attempt {attempt + 1}: {e}")
            
            # Специфичные сообщения для разных статусов
            if status == 401:
                return "❌ Ошибка авторизации: проверьте API ключ OpenRouter"
            elif status == 402:
                return "❌ Недостаточно средств на счету OpenRouter"
            elif status == 429:
                if attempt < 2:
                    logger.info(f"Rate limit hit, retrying in {delay}s")
                    await asyncio.sleep(delay)
                    delay *= 2
                    continue
                return "❌ Превышен лимит запросов. Попробуйте позже"
            elif status in (500, 502, 503, 504):
                if attempt < 2:
                    logger.info(f"Server error {status}, retrying in {delay}s")
                    await asyncio.sleep(delay)
                    delay *= 2
                    continue
                return f"❌ Ошибка AI сервиса ({status}). Попробуйте позже"
            else:
                return f"❌ HTTP ошибка {status}: {e.response.reason_phrase}"

        except httpx.TimeoutException as e:
            last_error = e
            logger.warning(f"Request timeout on attempt {attempt + 1}: {e}")
            
            if attempt < 2:
                await asyncio.sleep(delay)
                delay *= 2
                continue
            return "❌ Время ожидания истекло. Проверьте интернет соединение"
        
        except httpx.ConnectError as e:
            last_error = e
            logger.error(f"Connection error on attempt {attempt + 1}: {e}")
            
            if attempt < 2:
                await asyncio.sleep(delay)
                delay *= 2
                continue
            return "❌ Ошибка соединения с AI сервисом. Проверьте интернет"
        
        except Exception as e:
            last_error = e
            logger.error(f"Unexpected error on attempt {attempt + 1}: {type(e).__name__}: {e}")

            if attempt < 2:
                await asyncio.sleep(delay)
                delay *= 2
                continue
            return f"❌ Неожиданная ошибка: {type(e).__name__}"
    
    # Если все попытки неудачны
    logger.error(f"All attempts failed. Last error: {last_error}")
    return "❌ Не удалось получить ответ от AI после нескольких попыток"


async def cleanup_client() -> None:
    """Clean up the HTTP client pool."""
    from helpers.http_pool import cleanup_http_pool
    await cleanup_http_pool()