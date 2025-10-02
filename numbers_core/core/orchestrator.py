from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from numbers_core.calc.profile import calculate_core_profile
from numbers_core.intelligence.analysis import analyze_profile as run_ai_analysis
from numbers_core.intelligence.engine import AIClient, MockAIClient


@dataclass
class ProfileInput:
    """��������� ����� ������ ��� ����஥��� ��䨫�."""

    name: str
    birthdate: str



def build_profile(inp: ProfileInput) -> Dict[str, Any]:
    """��ନ��� �᫮��� ��䨫� �� �室�� �����."""

    normalized_birthdate = _normalize_birthdate(inp.birthdate)
    return calculate_core_profile(inp.name, normalized_birthdate)



def analyze_profile(profile: Dict[str, Any], ai: Optional[AIClient] = None) -> Dict[str, Any]:
    """����砥� ⥪�⮢� ������ ��䨫� �१ ��������� AI."""

    client: AIClient = ai if ai is not None else MockAIClient()
    text = run_ai_analysis(profile, client=client)
    return {"text": text}



def run(inp: ProfileInput, ai: Optional[AIClient] = None) -> Dict[str, Any]:
    """��᮪��஢����� �㭪��: ����� ��䨫� + ������."""

    profile = build_profile(inp)
    analysis = analyze_profile(profile, ai)
    return {"profile": profile, "analysis": analysis}



def _normalize_birthdate(value: str) -> str:
    """��⠥��� �ਢ��� ���� � �ଠ�� DD.MM.YYYY."""

    formats = ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%d-%m-%Y")
    for fmt in formats:
        try:
            dt = datetime.strptime(value.strip(), fmt)
            return dt.strftime("%d.%m.%Y")
        except ValueError:
            continue
    return value