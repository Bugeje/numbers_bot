from datetime import datetime
from config import settings

from calc.cycles import get_personal_month
from calc.math import extract_base
from helpers.concurrency import get_concurrency_manager
from .engine import ask_openrouter
from .prompts import (
    bridges_prompt,
    compatibility_prompt,
    cycles_prompt,
    days_prompt,
    extended_prompt,
    months_year_prompt,
    profile_prompt,
)
from .system_prompts import SYSTEM_PROMPTS


def _month_matches_core(profile: dict, personal_month: int) -> list[str]:
    pm = int(extract_base(personal_month))
    mapping = {
        "match-life_path": extract_base(profile.get("life_path")),
        "match-expression": extract_base(profile.get("expression")),
        "match-soul": extract_base(profile.get("soul")),
        "match-personality": extract_base(profile.get("personality")),
        "match-birthday": extract_base(profile.get("birthday")),
    }
    matches = []
    for label, val in mapping.items():
        try:
            if int(val) == pm:
                matches.append(label)
        except Exception:
            pass
    return matches


async def get_ai_analysis(core_profile: dict) -> str:
    """Основной анализ личности с контролем конкурентности и детальной диагностикой."""
    import logging
    logger = logging.getLogger(__name__)
    
    concurrency_manager = get_concurrency_manager()
    
    try:
        # Проверяем конфигурацию
        if not settings.ai.openrouter_api_key:
            logger.error("OpenRouter API key is missing")
            return "❌ Ошибка конфигурации: отсутствует API ключ. Обратитесь к администратору."
        
        # Проверяем входные данные
        if not core_profile or not isinstance(core_profile, dict):
            logger.error(f"Invalid core_profile data: {core_profile}")
            return "❌ Ошибка данных: некорректный профиль для анализа."
        
        logger.info(f"Starting AI analysis for profile: {list(core_profile.keys())}")
        
        async with concurrency_manager.ai_request_context():
            result = await ask_openrouter(
                SYSTEM_PROMPTS["profile"],
                profile_prompt(core_profile),
                temperature=settings.ai.temperature,
                max_tokens=settings.ai.max_tokens,
            )
            
            # Проверяем результат
            if not result or len(result.strip()) < 10:
                logger.warning(f"AI returned empty or very short response: {result}")
                return "❌ Получен пустой ответ от AI. Попробуйте позже."
            
            # Проверяем на ошибки API
            if result.startswith("❌"):
                logger.error(f"AI API error: {result}")
                return result
            
            logger.info("AI analysis completed successfully")
            return result
            
    except RuntimeError as e:
        logger.warning(f"Concurrency limit reached: {e}")
        return "⚠️ Система временно перегружена. Попробуйте через несколько секунд."
    except Exception as e:
        logger.error(f"Unexpected error in AI analysis: {type(e).__name__}: {e}")
        return f"❌ Ошибка при получении анализа: {type(e).__name__}. Попробуйте позже."


async def get_extended_analysis(extended_profile: dict) -> str:
    """Расширенный анализ с контролем конкурентности."""
    concurrency_manager = get_concurrency_manager()
    
    try:
        async with concurrency_manager.ai_request_context():
            return await ask_openrouter(
                SYSTEM_PROMPTS["extended"],
                extended_prompt(extended_profile),
                temperature=settings.ai.temperature,
                max_tokens=settings.ai.max_tokens,
            )
    except RuntimeError:
        return "Система временно перегружена. Попробуйте позже."
    except Exception:
        return "Ошибка при получении анализа."


async def get_bridges_analysis(bridges: dict) -> str:
    """Анализ мостов с контролем конкурентности."""
    concurrency_manager = get_concurrency_manager()
    
    try:
        async with concurrency_manager.ai_request_context():
            return await ask_openrouter(
                SYSTEM_PROMPTS["bridges"],
                bridges_prompt(bridges),
                temperature=settings.ai.temperature,
                max_tokens=settings.ai.max_tokens,
            )
    except RuntimeError:
        return "Система временно перегружена. Попробуйте позже."
    except Exception:
        return "Ошибка при получении анализа."


async def get_compatibility_interpretation(profile_a: dict, profile_b: dict) -> str:
    """Анализ совместимости с контролем конкурентности."""
    concurrency_manager = get_concurrency_manager()
    
    try:
        async with concurrency_manager.ai_request_context():
            return await ask_openrouter(
                SYSTEM_PROMPTS["compatibility"],
                compatibility_prompt(profile_a, profile_b),
                temperature=settings.ai.temperature,
                max_tokens=settings.ai.max_tokens,
            )
    except RuntimeError:
        return "Система временно перегружена. Попробуйте позже."
    except Exception:
        return "Ошибка при получении анализа."


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
    """Календарный анализ с контролем конкурентности."""
    concurrency_manager = get_concurrency_manager()
    
    try:
        async with concurrency_manager.ai_request_context():
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
    except RuntimeError:
        return "Система временно перегружена. Попробуйте позже."
    except Exception:
        return "Ошибка при получении анализа."


async def get_cycles_analysis(
    name: str,
    birthdate: str,
    life_path: str,
    personal_years: list,
    pinnacles: list,
    personal_year_blocks: dict
) -> str:
    """Получить ИИ анализ жизненных циклов с контролем конкурентности."""
    concurrency_manager = get_concurrency_manager()
    
    try:
        async with concurrency_manager.ai_request_context():
            return await ask_openrouter(
                SYSTEM_PROMPTS["cycles"],
                cycles_prompt(name, birthdate, life_path, personal_years, pinnacles, personal_year_blocks),
                temperature=settings.ai.temperature,
                max_tokens=settings.ai.max_tokens,
            )
    except RuntimeError:
        return "Система временно перегружена. Попробуйте позже."
    except Exception:
        return "Ошибка при получении анализа."


async def get_months_year_analysis(profile: dict, birthdate: str, personal_year: int, year: int | None = None) -> str:
    """Анализ месяцев года с контролем конкурентности."""
    if year is None:
        year = datetime.today().year
    months_map: dict[int,int] = {}
    matches_map: dict[int,list[str]] = {}
    for m in range(1, 13):
        pm = get_personal_month(birthdate=birthdate, year=year, month=m)
        months_map[m] = pm
        matches_map[m] = _month_matches_core(profile, pm)
    
    concurrency_manager = get_concurrency_manager()
    
    try:
        async with concurrency_manager.ai_request_context():
            return await ask_openrouter(
                SYSTEM_PROMPTS["months_year"],
                months_year_prompt(personal_year=personal_year, months_map=months_map, matches_map=matches_map),
                temperature=settings.ai.temperature,
                max_tokens=settings.ai.max_tokens,
            )
    except RuntimeError:
        return "Система временно перегружена. Попробуйте позже."
    except Exception:
        return "Ошибка при получении анализа."
