from numbers_core.core.orchestrator import ProfileInput, run


def test_run_returns_profile_and_analysis():
    """run возвращает словарь с профилем и анализом."""

    result = run(ProfileInput(name="Иван", birthdate="1990-01-01"))

    assert "profile" in result
    assert "analysis" in result
    assert "text" in result["analysis"]
    assert isinstance(result["analysis"]["text"], str)
