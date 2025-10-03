from functools import lru_cache

from .math import extract_base, reduce_number

MONTH_NAMES = [
    "Январь",
    "Февраль",
    "Март",
    "Апрель",
    "Май",
    "Июнь",
    "Июль",
    "Август",
    "Сентябрь",
    "Октябрь",
    "Ноябрь",
    "Декабрь",
]


def digit_sum(n: int) -> int:
    """Суммирует цифры числа."""

    return sum(int(d) for d in str(n))


@lru_cache(maxsize=64)
def generate_personal_month_matrix(birthdate: str) -> dict[int, dict[str, str]]:
    """Строит матрицу личных месяцев на 100 лет вперёд."""

    d, m, y = map(int, birthdate.strip().split("."))
    red_day = extract_base(reduce_number(d))
    red_month = extract_base(reduce_number(m))
    base_year = y

    matrix: dict[int, dict[str, str]] = {}
    for year in range(base_year, base_year + 100):
        red_year = extract_base(reduce_number(digit_sum(year)))
        personal_year = extract_base(reduce_number(red_day + red_month + red_year))
        month_row = {
            MONTH_NAMES[i]: reduce_number(personal_year + i + 1)
            for i in range(12)
        }
        matrix[year] = month_row
    return matrix


def generate_personal_month_cycle_table() -> dict[int, dict[str, str]]:
    """Готовит таблицу переходов личных месяцев для каждого личного года."""

    table: dict[int, dict[str, str]] = {}
    for py in range(1, 10):
        row = {MONTH_NAMES[i]: reduce_number(py + i + 1) for i in range(12)}
        table[py] = row
    return table


def get_personal_month(birthdate: str, year: int, month: int) -> str:
    """Возвращает личное число месяца для заданной даты."""

    matrix = generate_personal_month_matrix(birthdate)
    month_name = MONTH_NAMES[month - 1]
    return matrix[year][month_name]
