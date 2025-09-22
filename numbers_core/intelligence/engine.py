from typing import Protocol


class AIClient(Protocol):
    """Простой протокол клиента текстовой генерации."""

    def generate(self, prompt: str) -> str: ...


class MockAIClient:
    """Мок-реализация клиента, используемая по умолчанию."""

    def generate(self, prompt: str) -> str:
        return "Анализ временно недоступен: использована mock-реализация."
