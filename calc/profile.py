
from .mapping import VOWELS, calculate_sum_by_letters, name_to_numbers
from .math import reduce_number


def calculate_life_path_number(date_str: str) -> str:
    """Calculate life path number from date string in DD.MM.YYYY format."""
    parts = date_str.strip().split(".")
    day = reduce_number(int(parts[0]))
    month = reduce_number(int(parts[1]))
    year = reduce_number(int(parts[2]))
    total = sum(int(x.split("(")[0]) for x in [day, month, year])
    return reduce_number(total)


def calculate_birthday_number(date_str: str) -> str:
    """Calculate birthday number from date string."""
    return reduce_number(int(date_str.strip().split(".")[0]))


def calculate_expression_number(full_name: str) -> str:
    """Calculate expression number from full name."""
    return reduce_number(sum(name_to_numbers(full_name)))


def calculate_soul_number(full_name: str) -> str:
    """Calculate soul number from vowels in full name."""
    return reduce_number(calculate_sum_by_letters(full_name, lambda ch: ch in VOWELS))


def calculate_personality_number(full_name: str) -> str:
    """Calculate personality number from consonants in full name."""
    return reduce_number(calculate_sum_by_letters(full_name, lambda ch: ch not in VOWELS))


def calculate_destiny_number(soul: str, personality: str) -> str:
    """Calculate destiny number from soul and personality numbers."""
    soul_base = int(soul.split("(")[0])
    pers_base = int(personality.split("(")[0])
    return reduce_number(soul_base + pers_base)


def calculate_core_profile(full_name: str, birthdate: str) -> dict[str, str]:
    """Calculate complete core numerology profile."""
    life_path = calculate_life_path_number(birthdate)
    birthday = calculate_birthday_number(birthdate)
    expression = calculate_expression_number(full_name)
    soul = calculate_soul_number(full_name)
    personality = calculate_personality_number(full_name)
    destiny = calculate_destiny_number(soul, personality)

    return {
        "life_path": life_path,
        "birthday": birthday,
        "expression": expression,
        "soul": soul,
        "personality": personality,
        "destiny": destiny,
    }
