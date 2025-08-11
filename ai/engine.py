import httpx
from settings import settings

API_URL = f"{settings.OPENROUTER_BASE_URL}/chat/completions"
MODEL = "openai/gpt-4o"
DEBUG = False

async def ask_openrouter(system_prompt: str, user_prompt: str, *, 
                         temperature: float = None, max_tokens: int = None) -> str:
    import asyncio, httpx
    temperature = settings.AI_TEMPERATURE if temperature is None else temperature
    max_tokens = settings.AI_MAX_TOKENS if max_tokens is None else max_tokens

    if settings.OPENROUTER_API_KEY is None:
        return "❌ Ошибка: отсутствует API-ключ OpenRouter. Проверь .env."

    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "openai/gpt-4o",
        "temperature": temperature,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_prompt.strip()},
        ],
    }

    # ленивый общий клиент
    global _client
    if "_client" not in globals() or _client is None:
        _client = httpx.AsyncClient(timeout=httpx.Timeout(settings.HTTP_TIMEOUT))

    delay = 0.5
    for attempt in range(3):
        try:
            resp = await _client.post(API_URL, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            status = getattr(getattr(e, "response", None), "status_code", None)
            if attempt < 2 and (status in (429, 500, 502, 503, 504) or status is None):
                await asyncio.sleep(delay); delay *= 2; continue
            if status is not None:
                try:
                    reason = e.response.reason_phrase
                except Exception:
                    reason = "HTTP error"
                return f"❌ Ошибка {status}: {reason}"
            return f"[Сетевая ошибка AI: {e}]"
