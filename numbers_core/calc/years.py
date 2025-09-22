from datetime import datetime

from .math import extract_base, reduce_number


def digit_sum(n: int) -> int:
    """Возвращает сумму цифр числа."""

    return sum(int(d) for d in str(n))


def parse_components(birthdate: str) -> tuple[int, int, int]:
    """Разбивает дату рождения на день, месяц и год."""

    d, m, y = birthdate.strip().split(".")
    return int(d), int(m), int(y)


def calculate_personal_year(birthdate: str, target_year: int | None = None) -> str:
    """Вычисляет личный год для заданного календарного года."""

    if target_year is None:
        target_year = datetime.today().year

    day, month, _ = parse_components(birthdate)
    return reduce_number(
        extract_base(reduce_number(day))
        + extract_base(reduce_number(month))
        + extract_base(reduce_number(target_year))
    )


def get_personal_years(birthdate: str, years_count: int = 10) -> list[str]:
    """Возвращает список личных годов на несколько лет вперёд."""

    day, month, _ = parse_components(birthdate)
    start_year = datetime.today().year

    personal_years = []
    for offset in range(years_count):
        year = start_year + offset
        personal_year = reduce_number(
            extract_base(reduce_number(day))
            + extract_base(reduce_number(month))
            + extract_base(reduce_number(year))
        )
        personal_years.append(personal_year)
    return personal_years
