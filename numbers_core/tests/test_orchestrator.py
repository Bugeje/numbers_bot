import pytest

from numbers_core.core.orchestrator import ProfileInput, build_profile, run


def test_run_returns_profile_and_analysis():
    """run returns both the profile and the AI analysis container."""

    result = run(ProfileInput(name="Иван", birthdate="1990-01-01"))

    assert "profile" in result
    assert "analysis" in result
    assert "text" in result["analysis"]
    assert isinstance(result["analysis"]["text"], str)


def test_build_profile_rejects_empty_name():
    with pytest.raises(ValueError, match="full name"):
        build_profile(ProfileInput(name="   ", birthdate="1990-01-01"))


def test_build_profile_rejects_invalid_name_characters():
    with pytest.raises(ValueError, match="full name may contain only"):
        build_profile(ProfileInput(name="Иван 123", birthdate="1990-01-01"))


def test_build_profile_rejects_invalid_birthdate():
    with pytest.raises(ValueError, match="birthdate"):
        build_profile(ProfileInput(name="Иван Иванов", birthdate="not-a-date"))
