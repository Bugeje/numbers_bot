from numbers_core.calc.profile import calculate_core_profile


def test_calculate_core_profile_returns_expected_keys():
    """Профиль должен содержать ожидаемый набор показателей."""

    profile = calculate_core_profile("Иван Иванов", "01.01.1990")

    assert set(profile.keys()) == {"life_path", "birthday", "expression", "soul", "personality"}
