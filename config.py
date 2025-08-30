"""
Простая конфигурация без сложной валидации для быстрого запуска.
"""

import os
from typing import Any, Dict


def load_env_file():
    """Загружает .env файл если он существует."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass


class SimpleSettings:
    """Простые настройки без валидации."""
    
    def __init__(self):
        load_env_file()
        
        # Core settings
        self.environment = os.getenv('ENVIRONMENT', 'development')
        self.debug = os.getenv('DEBUG', 'false').lower() == 'true'
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        
        # HTTP settings - optimized for high concurrency
        self.http_timeout = float(os.getenv('HTTP_TIMEOUT', '45.0'))  # Increased for AI processing
        self.connection_pool_size = int(os.getenv('CONNECTION_POOL_SIZE', '200'))
        self.max_keepalive_connections = int(os.getenv('MAX_KEEPALIVE_CONNECTIONS', '100'))
        self.keepalive_expiry = float(os.getenv('KEEPALIVE_EXPIRY', '30.0'))
        
        # Performance settings - optimized for 100+ concurrent users
        self.max_concurrent_requests = int(os.getenv('MAX_CONCURRENT_REQUESTS', '200'))
        self.thread_pool_size = int(os.getenv('THREAD_POOL_SIZE', '100'))
        self.ai_semaphore_limit = int(os.getenv('AI_SEMAPHORE_LIMIT', '200'))
        self.pdf_semaphore_limit = int(os.getenv('PDF_SEMAPHORE_LIMIT', '100'))
        
        # Nested settings as objects
        self.telegram = self._create_telegram_settings()
        self.ai = self._create_ai_settings()
        self.database = self._create_database_settings()
        self.cache = self._create_cache_settings()
        self.security = self._create_security_settings()
    
    def _create_telegram_settings(self):
        """Создает настройки Telegram."""
        class TelegramSettings:
            def __init__(self):
                self.token = os.getenv('TELEGRAM_TOKEN', '')
                self.webhook_url = os.getenv('TELEGRAM_WEBHOOK_URL', '')
                self.webhook_secret = os.getenv('TELEGRAM_WEBHOOK_SECRET', '')
                self.max_connections = int(os.getenv('TELEGRAM_MAX_CONNECTIONS', '200'))
                self.read_timeout = float(os.getenv('TELEGRAM_READ_TIMEOUT', '30.0'))
                self.write_timeout = float(os.getenv('TELEGRAM_WRITE_TIMEOUT', '30.0'))
                self.connect_timeout = float(os.getenv('TELEGRAM_CONNECT_TIMEOUT', '10.0'))
                self.pool_timeout = float(os.getenv('TELEGRAM_POOL_TIMEOUT', '5.0'))
        
        return TelegramSettings()
    
    def _create_ai_settings(self):
        """Создает настройки AI."""
        class AISettings:
            def __init__(self):
                self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY', os.getenv('AI_OPENROUTER_API_KEY', ''))
                self.openrouter_base_url = os.getenv('OPENROUTER_BASE_URL', os.getenv('AI_OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1'))
                self.model = os.getenv('AI_MODEL', 'openai/gpt-4o')
                self.temperature = float(os.getenv('AI_TEMPERATURE', '0.7'))
                self.max_tokens = int(os.getenv('AI_MAX_TOKENS', '2048'))
                self.timeout = float(os.getenv('AI_TIMEOUT', '30.0'))
                self.max_retries = int(os.getenv('AI_MAX_RETRIES', '3'))
        
        return AISettings()
    
    def _create_database_settings(self):
        """Создает настройки базы данных."""
        class DatabaseSettings:
            def __init__(self):
                self.url = os.getenv('DB_URL', 'sqlite:///./numbers_bot.db')
                self.pool_size = int(os.getenv('DB_POOL_SIZE', '20'))
                self.max_overflow = int(os.getenv('DB_MAX_OVERFLOW', '10'))
                self.echo = os.getenv('DB_ECHO', 'false').lower() == 'true'
        
        return DatabaseSettings()
    
    def _create_cache_settings(self):
        """Создает настройки кеша."""
        class CacheSettings:
            def __init__(self):
                self.redis_url = os.getenv('CACHE_REDIS_URL', 'redis://localhost:6379/0')
                self.default_ttl = int(os.getenv('CACHE_DEFAULT_TTL', '3600'))
                self.max_connections = int(os.getenv('CACHE_MAX_CONNECTIONS', '50'))
        
        return CacheSettings()
    
    def _create_security_settings(self):
        """Создает настройки безопасности."""
        class SecuritySettings:
            def __init__(self):
                self.secret_key = os.getenv('SECURITY_SECRET_KEY', 'change-me-in-production-this-is-long-enough-key')
                self.rate_limit_per_minute = int(os.getenv('SECURITY_RATE_LIMIT_PER_MINUTE', '60'))
                self.max_file_size_mb = int(os.getenv('SECURITY_MAX_FILE_SIZE_MB', '10'))
        
        return SecuritySettings()
    
    @property
    def is_production(self) -> bool:
        """Проверяет, запущено ли в продакшене."""
        return self.environment.lower() == 'production'
    
    @property
    def is_development(self) -> bool:
        """Проверяет, запущено ли в разработке."""
        return self.environment.lower() == 'development'
    
    @property
    def is_testing(self) -> bool:
        """Проверяет, запущено ли в тестировании."""
        return self.environment.lower() == 'testing'
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Получает конфигурацию логирования."""
        import logging
        
        level = getattr(logging, self.log_level.upper(), logging.INFO)
        
        config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                },
                "detailed": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": self.log_level,
                    "formatter": "detailed" if self.debug else "standard",
                    "stream": "ext://sys.stdout",
                },
            },
            "loggers": {
                "": {  # root logger
                    "handlers": ["console"],
                    "level": level,
                    "propagate": False,
                },
                "httpx": {
                    "level": "WARNING",
                },
                "telegram": {
                    "level": "INFO",
                },
            },
        }
        
        if self.is_production:
            # Add file handler for production
            config["handlers"]["file"] = {
                "class": "logging.handlers.RotatingFileHandler",
                "level": self.log_level,
                "formatter": "detailed",
                "filename": "numbers_bot.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            }
            config["loggers"][""]["handlers"].append("file")
        
        return config


# Global settings instance
settings = SimpleSettings()