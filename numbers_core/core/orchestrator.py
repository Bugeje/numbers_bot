from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from numbers_core.calc.profile import calculate_core_profile
from numbers_core.intelligence.analysis import analyze as analyze_text
from numbers_core.intelligence.engine import AIClient, MockAIClient


@dataclass
class ProfileInput:
    """Минимальный набор данных для построения профиля."""

    name: str
    birthdate: str


def build_profile(inp: ProfileInput) -> Dict[str, Any]:
    """Формирует числовой профиль по входным данным."""

    normalized_birthdate = _normalize_birthdate(inp.birthdate)
    return calculate_core_profile(inp.name, normalized_birthdate)


def analyze_profile(profile: Dict[str, Any], ai: Optional[AIClient] = None) -> Dict[str, Any]:
    """Получает текстовый анализ профиля через подключённый AI."""

    client: AIClient = ai if ai is not None else MockAIClient()
    return analyze_text(profile, client)


def run(inp: ProfileInput, ai: Optional[AIClient] = None) -> Dict[str, Any]:
    """Высокоуровневая функция: расчёт профиля + анализ."""

    profile = build_profile(inp)
    analysis = analyze_profile(profile, ai)
    return {"profile": profile, "analysis": analysis}


def _normalize_birthdate(value: str) -> str:
    """Пытается привести дату к формату DD.MM.YYYY."""

    formats = ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%d-%m-%Y")
    for fmt in formats:
        try:
            dt = datetime.strptime(value.strip(), fmt)
            return dt.strftime("%d.%m.%Y")
        except ValueError:
            continue
    return value
