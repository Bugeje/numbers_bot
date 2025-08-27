import asyncio
import logging

import httpx

from config import settings

API_URL = f"{settings.ai.openrouter_base_url}/chat/completions"
MODEL = "openai/gpt-4o"
DEBUG = False

# Global client for connection pooling
_client: httpx.AsyncClient | None = None

logger = logging.getLogger(__name__)


async def ask_openrouter(
    system_prompt: str,
    user_prompt: str,
    *,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> str:
    """Ask OpenRouter API with proper error handling and retries."""
    temperature = settings.ai.temperature if temperature is None else temperature
    max_tokens = settings.ai.max_tokens if max_tokens is None else max_tokens

    if not settings.ai.openrouter_api_key:
        logger.error("Missing OpenRouter API key")
        return "❌ Ошибка: отсутствует API-ключ OpenRouter. Проверь .env."

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

    # Initialize client if needed
    global _client
    if _client is None:
        _client = httpx.AsyncClient(timeout=httpx.Timeout(settings.http_timeout))

    delay = 0.5
    for attempt in range(3):
        try:
            resp = await _client.post(API_URL, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

            if "choices" not in data or not data["choices"]:
                logger.error(f"Invalid API response: {data}")
                return "❌ Неожиданный ответ от API"

            return data["choices"][0]["message"]["content"].strip()

        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            logger.warning(f"HTTP error {status} on attempt {attempt + 1}")

            if attempt < 2 and status in (429, 500, 502, 503, 504):
                await asyncio.sleep(delay)
                delay *= 2
                continue

            try:
                reason = e.response.reason_phrase
            except Exception:
                reason = "HTTP error"
            return f"❌ Ошибка {status}: {reason}"

        except Exception as e:
            logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")

            if attempt < 2:
                await asyncio.sleep(delay)
                delay *= 2
                continue

            return f"❌ Сетевая ошибка: {e}"


async def cleanup_client() -> None:
    """Clean up the HTTP client."""
    global _client
    if _client:
        await _client.aclose()
        _client = None
