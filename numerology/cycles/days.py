from datetime import date
from calendar import monthrange
from numerology.utils import reduce_number, extract_base
from numerology.cycles.years import calculate_personal_year

def calculate_personal_day_base(birthdate: str, target_date: date) -> int:
    personal_year = extract_base(calculate_personal_year(birthdate, target_date.year))
    personal_month = extract_base(reduce_number(personal_year + target_date.month))
    calendar_day = extract_base(reduce_number(target_date.day))
    return extract_base(reduce_number(personal_month + calendar_day))

def generate_calendar_matrix(birthdate: str, year: int, month: int) -> list[list[dict]]:
    _, last_day = monthrange(year, month)
    start_date = date(year, month, 1)
    start_weekday = start_date.weekday()

    weeks, week = [], [None] * start_weekday
    for day in range(1, last_day + 1):
        date_obj = date(year, month, day)
        p_day = calculate_personal_day_base(birthdate, date_obj)
        week.append({"label": f"{day}\n{p_day}", "number": p_day})
        if len(week) == 7:
            weeks.append(week)
            week = []
    if week:
        week += [None] * (7 - len(week))
        weeks.append(week)
    return weeks
