# helpers/ai_analyzer.py
"""
Унифицированный AI анализатор для устранения дублирования кода в AI запросах.
"""
import logging
from typing import Optional, Callable, Any
from helpers.messages import M
from helpers.progress import Progress, PRESETS, action_typing


logger = logging.getLogger(__name__)


class AIAnalyzer:
    """Унифицированный анализатор AI с общей логикой обработки ошибок."""
    
    @staticmethod
    async def safe_analysis(
        ai_function: Callable, 
        *args, 
        fallback_message: str = None,
        **kwargs
    ) -> str:
        """
        Безопасное выполнение AI анализа с обработкой ошибок.
        
        Args:
            ai_function: Функция AI анализа
            fallback_message: Сообщение при ошибке (по умолчанию M.ERRORS.AI_GENERIC)
            *args, **kwargs: Аргументы для функции AI
        
        Returns:
            str: Результат анализа или сообщение об ошибке
        """
        if fallback_message is None:
            fallback_message = M.ERRORS.AI_GENERIC
        
        try:
            logger.debug(f"Starting AI analysis: {ai_function.__name__}")
            result = await ai_function(*args, **kwargs)
            
            # Проверяем результат на ошибки
            if M.is_ai_error(result):
                logger.warning(f"AI function returned error: {result}")
                return fallback_message
            
            if not result or len(result.strip()) < 10:
                logger.warning("AI returned empty or very short response")
                return fallback_message
            
            logger.debug(f"AI analysis successful: {len(result)} characters")
            return result
            
        except Exception as e:
            logger.error(f"AI analysis failed: {ai_function.__name__}: {e}")
            return fallback_message
    
    @staticmethod
    async def analysis_with_progress(
        update, 
        ai_function: Callable, 
        *args,
        progress_presets: list = None,
        **kwargs
    ) -> tuple[str, Progress]:
        """
        AI анализ с прогресс-индикатором.
        
        Returns:
            tuple[str, Progress]: (результат_анализа, прогресс_объект)
        """
        if progress_presets is None:
            progress_presets = PRESETS["ai"]
        
        # Запускаем прогресс
        await action_typing(update.effective_chat)
        progress = await Progress.start(update, progress_presets[0])
        await progress.animate(progress_presets, delay=0.6)
        
        # Выполняем анализ
        result = await AIAnalyzer.safe_analysis(ai_function, *args, **kwargs)
        
        return result, progress


class AnalysisCache:
    """Простой кеш для AI анализов (опционально)."""
    
    def __init__(self, max_size: int = 100):
        self._cache = {}
        self._max_size = max_size
    
    def _make_key(self, func_name: str, *args, **kwargs) -> str:
        """Создание ключа кеша из аргументов."""
        key_parts = [func_name]
        key_parts.extend(str(arg) for arg in args)
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        return "|".join(key_parts)
    
    def get(self, func_name: str, *args, **kwargs) -> Optional[str]:
        """Получение из кеша."""
        key = self._make_key(func_name, *args, **kwargs)
        return self._cache.get(key)
    
    def set(self, func_name: str, result: str, *args, **kwargs):
        """Сохранение в кеш."""
        if len(self._cache) >= self._max_size:
            # Простая очистка - удаляем первый элемент
            first_key = next(iter(self._cache))
            del self._cache[first_key]
        
        key = self._make_key(func_name, *args, **kwargs)
        self._cache[key] = result
    
    def clear(self):
        """Очистка кеша."""
        self._cache.clear()


# Глобальный экземпляр кеша (опционально)
analysis_cache = AnalysisCache()


class CachedAIAnalyzer(AIAnalyzer):
    """AI анализатор с кешированием результатов."""
    
    @staticmethod
    async def cached_analysis(
        ai_function: Callable, 
        *args, 
        use_cache: bool = True,
        fallback_message: str = None,
        **kwargs
    ) -> str:
        """AI анализ с кешированием."""
        func_name = ai_function.__name__
        
        # Проверяем кеш
        if use_cache:
            cached_result = analysis_cache.get(func_name, *args, **kwargs)
            if cached_result:
                logger.debug(f"Using cached AI result for {func_name}")
                return cached_result
        
        # Выполняем анализ
        result = await AIAnalyzer.safe_analysis(
            ai_function, *args, fallback_message=fallback_message, **kwargs
        )
        
        # Сохраняем в кеш (только успешные результаты)
        if use_cache and result != (fallback_message or M.ERRORS.AI_GENERIC):
            analysis_cache.set(func_name, result, *args, **kwargs)
        
        return result