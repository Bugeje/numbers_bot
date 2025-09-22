from .math import extract_base, reduce_number
from .mapping import name_to_numbers
from .profile import (
    calculate_expression_number,
    calculate_life_path_number,
)


def calculate_balance(name: str) -> str:
    """Число баланса по инициалам в имени."""

    parts = name.upper().split()
    initials = [part[0] for part in parts if part]
    values = []
    for ch in initials:
        numbers = name_to_numbers(ch)
        if numbers:
            values.append(numbers[0])
    return reduce_number(sum(values)) if values else "0"


def calculate_growth(birthdate: str) -> str:
    """Число роста (по месяцу рождения)."""

    month = int(birthdate.split(".")[1])
    return reduce_number(month)


def calculate_realization(name: str, birthdate: str) -> str:
    """Число реализации как сумма выражения и жизненного пути."""

    expression = calculate_expression_number(name)
    life_path = calculate_life_path_number(birthdate)
    return reduce_number(extract_base(expression) + extract_base(life_path))


def calculate_mind(name: str, birthdate: str) -> str:
    """Число разума: первое имя + день рождения."""

    parts = name.strip().split()
    first_name = parts[1] if len(parts) > 1 else parts[0]
    name_value = reduce_number(sum(name_to_numbers(first_name)))
    day = int(birthdate.split(".")[0])
    birth_value = reduce_number(day)
    return reduce_number(extract_base(name_value) + extract_base(birth_value))


def calculate_extended_profile(name: str, birthdate: str) -> dict[str, str]:
    """Формирует расширенный профиль на основе дополнительных чисел."""

    return {
        "balance": calculate_balance(name),
        "growth": calculate_growth(birthdate),
        "realization": calculate_realization(name, birthdate),
        "mind": calculate_mind(name, birthdate),
    }
