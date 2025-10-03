from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import warnings

from .prompts.loader import load_prompt
from .openrouter_client import OpenRouterClient


PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"
DEFAULT_ERROR_MESSAGE = "Анализ временно недоступен."


def analyze_profile(
    profile: Dict[str, Any],
    lang: str = "ru",
    client: Any | None = None,
    model: str = "openai/gpt-5-chat",
) -> str:
    system_path = PROMPTS_DIR / f"system.{lang}.md"
    user_path = PROMPTS_DIR / f"numerology.{lang}.md"
    system, user = load_prompt(str(user_path), str(system_path), profile)

    try:
        client = client or OpenRouterClient(model=model)

        if hasattr(client, "chat"):
            text = client.chat(system, user)
        elif hasattr(client, "analyze_profile"):
            text = client.analyze_profile(profile)
        elif hasattr(client, "generate"):
            text = client.generate(system.strip() + "\n\n" + user.strip())
        else:
            raise TypeError(
                "client must expose chat(system,user), analyze_profile(profile) or generate(prompt)"
            )

        cleaned = (text or "").strip()
        if not cleaned:
            raise ValueError("analysis text is empty")
        return cleaned
    except Exception as exc:
        return f"{DEFAULT_ERROR_MESSAGE} Причина: {exc}"


def analyze_profile_with_ai(profile: Dict[str, Any], ai_client: Any = None, lang: str = "ru") -> str:
    warnings.warn("Используй analyze_profile(..., client=ai_client)", DeprecationWarning)
    return analyze_profile(profile, lang=lang, client=ai_client)
