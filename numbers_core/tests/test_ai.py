from numbers_core.core.orchestrator import ProfileInput, run
from numbers_core.intelligence.analysis import DEFAULT_ERROR_MESSAGE


class DummyAIClient:
    """Return a predictable response instead of reaching OpenRouter."""

    def chat(self, system: str, user: str) -> str:
        return "Dummy AI analysis"


class EmptyAIClient:
    """Simulate a client that returns blank text, triggering fallback handling."""

    def chat(self, system: str, user: str) -> str:
        return "   "


def test_run_uses_provided_ai_client_without_network():
    """run should use the injected client and avoid network access."""

    inp = ProfileInput(name="John Doe", birthdate="1990-01-01")

    result = run(inp, ai=DummyAIClient())

    assert result["analysis"]["text"] == "Dummy AI analysis"
    assert set(result["profile"].keys()) == {"life_path", "birthday", "expression", "soul", "personality"}


def test_run_returns_fallback_message_for_empty_response():
    """If the AI client returns empty text, the orchestrator should fall back to a stub message."""

    inp = ProfileInput(name="John Doe", birthdate="1990-01-01")

    result = run(inp, ai=EmptyAIClient())

    assert result["analysis"]["text"].startswith(DEFAULT_ERROR_MESSAGE)
