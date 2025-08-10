from datetime import datetime
from numerology.utils import reduce_number, extract_base

def digit_sum(n: int) -> int:
    return sum(int(d) for d in str(n))

def parse_components(birthdate: str) -> tuple[int, int, int]:
    d, m, y = birthdate.strip().split(".")
    return int(d), int(m), int(y)

def calculate_personal_year(birthdate: str, target_year: int = None) -> str:
    if target_year is None:
        target_year = datetime.today().year
    day, month, _ = parse_components(birthdate)
    return reduce_number(
        extract_base(reduce_number(day)) +
        extract_base(reduce_number(month)) +
        extract_base(reduce_number(digit_sum(target_year)))
    )

def generate_personal_year_table(birthdate: str) -> dict:
    day, month, year = parse_components(birthdate)
    red_day = extract_base(reduce_number(day))
    red_month = extract_base(reduce_number(month))
    return {
        y: reduce_number(red_day + red_month + extract_base(reduce_number(digit_sum(y))))
        for y in range(year, year + 100)
    }

def calculate_pinnacles_with_periods(birthdate: str, life_path_str: str) -> dict:
    day, month, year = parse_components(birthdate)
    red_day = extract_base(reduce_number(day))
    red_month = extract_base(reduce_number(month))
    red_year = extract_base(reduce_number(year))
    red_life_path = extract_base(life_path_str)

    p1 = reduce_number(red_day + red_month)
    p2 = reduce_number(red_day + red_year)
    p3 = reduce_number(extract_base(p1) + extract_base(p2))
    p4 = reduce_number(red_month + red_year)

    end1 = year + 36 - red_life_path
    return {
        f"Вершина 1 ({year}–{end1})": p1,
        f"Вершина 2 ({end1+1}–{end1+9})": p2,
        f"Вершина 3 ({end1+10}–{end1+18})": p3,
        f"Вершина 4 ({end1+19}–{year+100})": p4,
    }

def split_years_by_pinnacles(birthdate: str) -> list[dict]:
    day, month, year = parse_components(birthdate)
    red_day = extract_base(reduce_number(day))
    red_month = extract_base(reduce_number(month))
    red_year = extract_base(reduce_number(year))
    red_life_path = extract_base(reduce_number(red_day + red_month + red_year))

    end1 = year + 36 - red_life_path
    end2, end3, end4 = end1 + 9, end1 + 18, year + 100
    full_table = generate_personal_year_table(birthdate)
    return [
        {y: v for y, v in full_table.items() if year <= y <= end1},
        {y: v for y, v in full_table.items() if end1 < y <= end2},
        {y: v for y, v in full_table.items() if end2 < y <= end3},
        {y: v for y, v in full_table.items() if end3 < y <= end4},
    ]
