from dataclasses import dataclass


@dataclass
class Settings:
    """Lightweight configuration container for the core package."""

    locale: str = "ru-RU"
    default_analysis_language: str = "ru"


settings = Settings()
