from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    TELEGRAM_TOKEN: str = Field(..., min_length=1)
    OPENROUTER_API_KEY: str = Field(..., min_length=0)
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    AI_TEMPERATURE: float = 0.7
    AI_MAX_TOKENS: int = 2048
    HTTP_TIMEOUT: float = 30.0
    
    # Performance settings for high concurrent usage
    MAX_CONCURRENT_REQUESTS: int = 50  # Limit concurrent API requests
    THREAD_POOL_SIZE: int = 20  # For CPU-intensive tasks
    CONNECTION_POOL_SIZE: int = 100  # HTTP connection pool

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
