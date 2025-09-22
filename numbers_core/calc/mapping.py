PIFAGOR_TABLE = {
    "А": 1,
    "И": 1,
    "С": 1,
    "Ь": 1,
    "Б": 2,
    "Й": 2,
    "Т": 2,
    "Ы": 2,
    "В": 3,
    "К": 3,
    "У": 3,
    "Э": 3,
    "Г": 4,
    "Л": 4,
    "Ф": 4,
    "Ю": 4,
    "Д": 5,
    "М": 5,
    "Х": 5,
    "Я": 5,
    "Е": 6,
    "Ё": 6,
    "Н": 6,
    "Ц": 6,
    "Ж": 7,
    "О": 7,
    "Ч": 7,
    "З": 8,
    "П": 8,
    "Ш": 8,
    "Р": 9,
    "Щ": 9,
}

VOWELS = set("АЕЁИОУЫЭЮЯ")


def name_to_numbers(name: str) -> list[int]:
    """Преобразует имя в последовательность чисел по таблице Пифагора."""

    return [PIFAGOR_TABLE[ch] for ch in name.upper() if ch in PIFAGOR_TABLE]


def calculate_sum_by_letters(name: str, filter_func=None) -> int:
    """Суммирует значения букв с учётом дополнительного фильтра."""

    letters = name.upper()
    return sum(
        PIFAGOR_TABLE[ch]
        for ch in letters
        if ch in PIFAGOR_TABLE and (filter_func(ch) if filter_func else True)
    )
