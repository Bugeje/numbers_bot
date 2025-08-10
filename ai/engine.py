import os
import httpx
from config import OPENROUTER_API_KEY, AI_TEMPERATURE, AI_MAX_TOKENS

API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-4o"
DEBUG = True

async def ask_openrouter(system_prompt: str, user_prompt: str, temperature: float = AI_TEMPERATURE, max_tokens: int = AI_MAX_TOKENS) -> str:
    if not OPENROUTER_API_KEY:
        return "❌ Ошибка: отсутствует API-ключ OpenRouter. Проверь .env."

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "X-Title": "NumerologyBot"
    }

    payload = {
        "model": MODEL,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_prompt.strip()}
        ]
    }

    if DEBUG:
        print("\n[AI PROMPT DEBUG]")
        print("System:", system_prompt.strip())
        print("User:", user_prompt.strip())
        print("[END DEBUG]\n")

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(API_URL, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip()
    except httpx.HTTPStatusError as e:
        return f"❌ Ошибка {e.response.status_code}: {e.response.reason_phrase}"
    except Exception as e:
        return f"[Сетевая ошибка AI: {e}]"

