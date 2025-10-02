from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import warnings

from .prompts.loader import load_prompt
from .openrouter_client import OpenRouterClient


PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"


def analyze_profile(
    profile: Dict[str, Any],
    lang: str = "ru",
    client: Any | None = None,
    model: str = "openai/gpt-5-chat",
) -> str:
    system_path = PROMPTS_DIR / f"system.{lang}.md"
    user_path = PROMPTS_DIR / f"numerology.{lang}.md"
    system, user = load_prompt(str(user_path), str(system_path), profile)

    client = client or OpenRouterClient(model=model)

    try:
        if hasattr(client, "chat"):
            text = client.chat(system, user)
        elif hasattr(client, "analyze_profile"):
            text = client.analyze_profile(profile)
        else:
            raise TypeError("client must have .chat(system,user) or .analyze_profile(profile)")
        return (text or "").strip() or "Анализ временно недоступен."
    except Exception as exc:
        return f"Анализ временно недоступен: {exc}"



def analyze_profile_with_ai(profile: Dict[str, Any], ai_client: Any = None, lang: str = "ru") -> str:
    warnings.warn("Используй analyze_profile(..., client=ai_client)", DeprecationWarning)
    return analyze_profile(profile, lang=lang, client=ai_client)