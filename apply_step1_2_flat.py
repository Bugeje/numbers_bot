# apply_step1_2_flat.py
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path.cwd()
assert (ROOT / "bot.py").exists(), "Запусти скрипт из корня репозитория (где лежит bot.py)."

def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def patch_file(path: Path, transform):
    txt = path.read_text(encoding="utf-8", errors="replace")
    new = transform(txt)
    if new != txt:
        path.write_text(new, encoding="utf-8")
        return True
    return False

# 1) settings.py (новый файл в корне)
SETTINGS = """from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    TELEGRAM_TOKEN: str = Field(..., min_length=1)
    OPENROUTER_API_KEY: str = Field(..., min_length=0)
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    AI_TEMPERATURE: float = 0.7
    AI_MAX_TOKENS: int = 2048
    HTTP_TIMEOUT: float = 30.0

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
"""
write(ROOT / "settings.py", SETTINGS)

# 2) handlers/states.py → IntEnum
STATE_FILE = ROOT / "handlers" / "states.py"
if STATE_FILE.exists():
    STATES = """from enum import IntEnum

class State(IntEnum):
    ASK_NAME = 0
    ASK_BIRTHDATE = 1
    EXTENDED_ANALYSIS = 2
    ASK_PARTNER_NAME = 3
    ASK_PARTNER_BIRTHDATE = 4
"""
    write(STATE_FILE, STATES)

# 3) Заменяем константы на State.*, добавляем импорт State где нужно
def fix_handler(text: str) -> str:
    # импорт State
    if "from handlers.states import State" not in text and "handlers.states" in text or "ASK_NAME" in text:
        text = "from handlers.states import State\n" + text
    # убрать старые импорты типа ASK_*
    text = re.sub(r"from\s+handlers\.states\s+import\s+(ASK_[A-Z_]+(?:\s*,\s*ASK_[A-Z_]+)*)", "from handlers.states import State", text)
    # локальные присваивания констант удалить
    text = re.sub(r"^\s*ASK_[A-Z_]+\s*=\s*\d+\s*$", "", text, flags=re.MULTILINE)
    # замены на State.*
    for name in ["ASK_NAME","ASK_BIRTHDATE","EXTENDED_ANALYSIS","ASK_PARTNER_NAME","ASK_PARTNER_BIRTHDATE"]:
        text = re.sub(rf"\b{name}\b", f"State.{name}", text)
    # типичный кейс "return 1" → ASK_BIRTHDATE
    text = re.sub(r"\breturn\s+1\b", "return State.ASK_BIRTHDATE", text)
    # убрать одинокие "State."
    text = re.sub(r"^\s*State\.\s*$", "", text, flags=re.MULTILINE)
    return text

for p in (ROOT / "handlers").glob("*.py"):
    if p.name != "states.py":
        patch_file(p, fix_handler)

# bot.py тоже может содержать ссылки на константы
BOT = ROOT / "bot.py"
patch_file(BOT, fix_handler)

# 4) ai/engine.py — общий httpx-клиент + settings
ENGINE = ROOT / "ai" / "engine.py"
def fix_engine(text: str) -> str:
    text = re.sub(r"^import os\s*\n", "", text, flags=re.MULTILINE)
    text = text.replace("from config import OPENROUTER_API_KEY, AI_TEMPERATURE, AI_MAX_TOKENS",
                        "from settings import settings")
    text = re.sub(r'API_URL\s*=\s*".*?/chat/completions"', 'API_URL = f"{settings.OPENROUTER_BASE_URL}/chat/completions"', text)
    # полная функция ask_openrouter
    text = re.sub(r"async def ask_openrouter[\s\S]+", 
r'''async def ask_openrouter(system_prompt: str, user_prompt: str, *, 
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
''', text)
    # убедимся, что DEBUG не шумит
    text = text.replace("DEBUG = True", "DEBUG = False")
    # добавим _client, если его нет
    if "_client" not in text:
        text = "import httpx\n_client = None\n" + text
    return text
patch_file(ENGINE, fix_engine)

# 5) ai/analysis.py — config → settings
AN = ROOT / "ai" / "analysis.py"
def fix_analysis(text: str) -> str:
    text = text.replace("from config import AI_TEMPERATURE, AI_MAX_TOKENS",
                        "from settings import settings")
    text = re.sub(r"temperature\s*=\s*AI_TEMPERATURE", "temperature=settings.AI_TEMPERATURE", text)
    text = re.sub(r"max_tokens\s*=\s*AI_MAX_TOKENS", "max_tokens=settings.AI_MAX_TOKENS", text)
    return text
patch_file(AN, fix_analysis)

# 6) bot.py — токен и тайм-ауты из settings
def fix_bot(text: str) -> str:
    if "from settings import settings" not in text:
        text = text.replace("from telegram.request import HTTPXRequest",
                            "from telegram.request import HTTPXRequest\nfrom settings import settings")
    text = re.sub(r"from\s+config\s+import\s+TELEGRAM_TOKEN\s*\n", "", text)
    text = text.replace(".token(TELEGRAM_TOKEN)", ".token(settings.TELEGRAM_TOKEN)")
    text = re.sub(r"HTTPXRequest\([^)]*\)",
                  "HTTPXRequest(read_timeout=settings.HTTP_TIMEOUT, write_timeout=settings.HTTP_TIMEOUT, connect_timeout=settings.HTTP_TIMEOUT, pool_timeout=settings.HTTP_TIMEOUT)",
                  text, flags=re.DOTALL)
    return text
patch_file(BOT, fix_bot)

# 7) requirements.txt — добавить pydantic-settings
REQ = ROOT / "requirements.txt"
req = REQ.read_text(encoding="utf-8", errors="replace")
if "pydantic-settings" not in req:
    req += ("\n" if not req.endswith("\n") else "") + "pydantic-settings\n"
write(REQ, req)

print("✅ Готово: шаги 1–2 применены под плоскую структуру.")
