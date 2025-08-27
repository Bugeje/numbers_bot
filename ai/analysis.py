from config import settings

from .engine import ask_openrouter
from .prompts import (
    bridges_prompt,
    compatibility_prompt,
    days_prompt,
    extended_prompt,
    profile_prompt,
)
from .system_prompts import SYSTEM_PROMPTS


async def get_ai_analysis(core_profile: dict) -> str:
    return await ask_openrouter(
        SYSTEM_PROMPTS["profile"],
        profile_prompt(core_profile),
        temperature=settings.ai.temperature,
        max_tokens=settings.ai.max_tokens,
    )


async def get_extended_analysis(extended_profile: dict) -> str:
    return await ask_openrouter(
        SYSTEM_PROMPTS["extended"],
        extended_prompt(extended_profile),
        temperature=settings.ai.temperature,
        max_tokens=settings.ai.max_tokens,
    )


async def get_bridges_analysis(bridges: dict) -> str:
    return await ask_openrouter(
        SYSTEM_PROMPTS["bridges"],
        bridges_prompt(bridges),
        temperature=settings.ai.temperature,
        max_tokens=settings.ai.max_tokens,
    )


async def get_compatibility_interpretation(profile_a: dict, profile_b: dict) -> str:
    return await ask_openrouter(
        SYSTEM_PROMPTS["compatibility"],
        compatibility_prompt(profile_a, profile_b),
        temperature=settings.ai.temperature,
        max_tokens=settings.ai.max_tokens,
    )


def get_active_components(matches_by_day: dict) -> tuple[list[str], list[str], list[str]]:
    single_components = set()
    gradients = set()
    fusion_groups = set()

    for comps in matches_by_day.values():
        labeled = [f"match-{comp}" for comp in comps]
        if len(labeled) == 1:
            single_components.add(labeled[0])
        elif 2 <= len(labeled) <= 5:
            gradient = "+".join(sorted(labeled))
            gradients.add(gradient)
            fusion_groups.add(gradient)

    return sorted(single_components), sorted(gradients), sorted(fusion_groups)


async def get_calendar_analysis(
    profile: dict,
    month_name: str,
    matches_by_day: dict,
    single_components: list[str],
    gradients: list[str],
    fusion_groups: list[str],
    personal_month: int = None,
) -> str:

    return await ask_openrouter(
        SYSTEM_PROMPTS["days"],
        days_prompt(
            month_name=month_name,
            personal_month=personal_month,
            single_components=single_components,
            gradients=gradients,
            fusion_groups=fusion_groups,
        ),
        temperature=settings.ai.temperature,
        max_tokens=settings.ai.max_tokens,
    )
