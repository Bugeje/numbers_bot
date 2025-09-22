from typing import Any, Dict

from .engine import AIClient


def analyze(profile: Dict[str, Any], ai: AIClient) -> Dict[str, Any]:
    """Генерирует текстовый разбор числового профиля."""

    prompt = _make_prompt(profile)
    text = ai.generate(prompt)
    return {"text": text}


def _make_prompt(profile: Dict[str, Any]) -> str:
    """Собирает человекочитаемый промпт со значениями профиля."""

    header = "Сформируй краткий разбор числового профиля на русском языке."
    lines = [header, "Исходные данные:"]
    for key, value in profile.items():
        lines.append(f"- {key}: {value}")
    return "\n".join(lines)
