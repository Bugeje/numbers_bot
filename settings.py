from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    TELEGRAM_TOKEN: str = Field(..., min_length=1)
    OPENROUTER_API_KEY: str = Field(..., min_length=0)
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    AI_TEMPERATURE: float = 0.7
    AI_MAX_TOKENS: int = 2048
    HTTP_TIMEOUT: float = 30.0

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
