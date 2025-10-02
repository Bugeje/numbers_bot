from typing import Protocol


class AIClient(Protocol):
    """Простой протокол клиента текстовой генерации."""

    def generate(self, prompt: str) -> str: ...


class MockAIClient:
    """Мок-реализация клиента, используемая по умолчанию."""

    def generate(self, prompt: str) -> str:
        return "Анализ временно недоступен: использована mock-реализация."

    def chat(self, system: str, user: str) -> str:
        return self.generate(system.strip() + "\n\n" + user.strip())
