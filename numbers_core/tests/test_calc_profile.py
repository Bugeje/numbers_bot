from datetime import date

import pytest

from numbers_core.calc.days import calculate_personal_day_base
from numbers_core.calc.months import get_personal_month
from numbers_core.calc.profile import calculate_core_profile


@pytest.mark.parametrize(
    "full_name,birthdate",
    [
        ("Иван Иванов", "01.01.1990"),
        ("Анна-Мария Петрова", "15.07.1985"),
    ],
)
def test_calculate_core_profile_returns_expected_keys(full_name, birthdate):
    """Профиль должен содержать ожидаемый набор показателей."""

    profile = calculate_core_profile(full_name, birthdate)

    assert set(profile.keys()) == {"life_path", "birthday", "expression", "soul", "personality"}


def test_calculate_personal_day_base_known_example():
    day_number = calculate_personal_day_base("01.01.1990", date(2024, 6, 15))
    assert isinstance(day_number, int)
    assert 1 <= day_number <= 9


def test_get_personal_month_reuses_cached_matrix():
    month_value = get_personal_month("01.01.1990", 2025, 3)
    second_value = get_personal_month("01.01.1990", 2025, 3)
    assert isinstance(month_value, str)
    assert month_value == second_value
