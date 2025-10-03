from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from numbers_core.calc.profile import calculate_core_profile
from numbers_core.intelligence.analysis import analyze_profile as run_ai_analysis
from numbers_core.intelligence.engine import AIClient, MockAIClient


@dataclass
class ProfileInput:
    """Minimal container for the data supplied by a user."""

    name: str
    birthdate: str



def build_profile(inp: ProfileInput) -> Dict[str, Any]:
    """Return a numerology profile built from validated input."""

    normalized_name = _normalize_name(inp.name)
    normalized_birthdate = _normalize_birthdate(inp.birthdate)
    return calculate_core_profile(normalized_name, normalized_birthdate)



def analyze_profile(profile: Dict[str, Any], ai: Optional[AIClient] = None) -> Dict[str, Any]:
    """Produce AI-generated analysis for an existing profile."""

    client: AIClient = ai if ai is not None else MockAIClient()
    text = run_ai_analysis(profile, client=client)
    return {"text": text}



def run(inp: ProfileInput, ai: Optional[AIClient] = None) -> Dict[str, Any]:
    """Full pipeline: calculate profile and optionally run AI analysis."""

    profile = build_profile(inp)
    analysis = analyze_profile(profile, ai)
    return {"profile": profile, "analysis": analysis}



def _normalize_name(value: str) -> str:
    """Ensure the name is present, readable and contains letters."""

    if value is None:
        raise ValueError("full name must be provided")

    parts = [part for part in value.strip().split() if part]
    if not parts:
        raise ValueError("full name must be provided")

    normalized = " ".join(parts)
    if not any(ch.isalpha() for ch in normalized):
        raise ValueError("full name must contain letters")

    for part in parts:
        if not all(ch.isalpha() or ch in "-'" for ch in part):
            raise ValueError("full name may contain only letters, hyphen or apostrophe")
    return normalized



def _normalize_birthdate(value: str) -> str:
    """Normalize supported date formats or raise a descriptive error."""

    if value is None:
        raise ValueError("birthdate must be provided")

    raw = value.strip()
    if not raw:
        raise ValueError("birthdate must be provided")

    formats = ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%d-%m-%Y")
    for fmt in formats:
        try:
            dt = datetime.strptime(raw, fmt)
            return dt.strftime("%d.%m.%Y")
        except ValueError:
            continue

    raise ValueError(
        "birthdate must be in one of the formats: YYYY-MM-DD, DD.MM.YYYY, DD/MM/YYYY, DD-MM-YYYY"
    )
