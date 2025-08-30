#!/usr/bin/env python3
# test_ai_analyzer_compatibility.py
"""
Тест для проверки совместимости AIAnalyzer с существующими AI функциями.
"""

import sys
import os
import asyncio
from unittest.mock import Mock, AsyncMock

# Добавляем корень проекта в PATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class MockUpdate:
    def __init__(self):
        self.effective_chat = Mock()
        self.effective_chat.id = 12345

async def test_ai_analyzer_compatibility():
    """Тест совместимости AIAnalyzer с существующими AI функциями."""
    print("🔍 Тест совместимости AIAnalyzer...")
    
    try:
        # Импортируем AIAnalyzer
        from helpers.ai_analyzer import AIAnalyzer, CachedAIAnalyzer, AnalysisCache
        from helpers.messages import M
        
        print("  Тест 1: AIAnalyzer.safe_analysis с успешным результатом")
        async def mock_ai_function_success(profile):
            return "Успешный AI анализ"
        
        try:
            result = await AIAnalyzer.safe_analysis(mock_ai_function_success, {"test": "profile"})
            if result == "Успешный AI анализ":
                print("    ✅ AIAnalyzer успешно обрабатывает успешные результаты")
            else:
                print(f"    ❌ Неожиданный результат: {result}")
                return False
        except Exception as e:
            print(f"    ❌ Ошибка: {e}")
            return False
        
        print("  Тест 2: AIAnalyzer.safe_analysis с ошибкой")
        async def mock_ai_function_error(profile):
            raise Exception("Ошибка AI")
        
        try:
            result = await AIAnalyzer.safe_analysis(mock_ai_function_error, {"test": "profile"})
            # Проверяем, что возвращается сообщение об ошибке по умолчанию
            if result == M.ERRORS.AI_GENERIC:
                print("    ✅ AIAnalyzer корректно обрабатывает ошибки")
            else:
                print(f"    ❌ Неожиданный результат при ошибке: {result}")
                return False
        except Exception as e:
            print(f"    ❌ Необработанная ошибка: {e}")
            return False
        
        print("  Тест 3: AIAnalyzer.safe_analysis с пользовательским сообщением об ошибке")
        async def mock_ai_function_error_custom(profile):
            raise Exception("Ошибка AI")
        
        try:
            custom_error_message = "Пользовательская ошибка"
            result = await AIAnalyzer.safe_analysis(
                mock_ai_function_error_custom, 
                {"test": "profile"},
                fallback_message=custom_error_message
            )
            # Проверяем, что возвращается пользовательское сообщение об ошибке
            if result == custom_error_message:
                print("    ✅ AIAnalyzer корректно обрабатывает пользовательские сообщения об ошибках")
            else:
                print(f"    ❌ Неожиданный результат при пользовательской ошибке: {result}")
                return False
        except Exception as e:
            print(f"    ❌ Необработанная ошибка: {e}")
            return False
        
        print("  Тест 4: AIAnalyzer.safe_analysis с пустым результатом")
        async def mock_ai_function_empty(profile):
            return ""
        
        try:
            result = await AIAnalyzer.safe_analysis(mock_ai_function_empty, {"test": "profile"})
            # Проверяем, что возвращается сообщение об ошибке по умолчанию для пустого результата
            if result == M.ERRORS.AI_GENERIC:
                print("    ✅ AIAnalyzer корректно обрабатывает пустые результаты")
            else:
                print(f"    ❌ Неожиданный результат при пустом ответе: {result}")
                return False
        except Exception as e:
            print(f"    ❌ Необработанная ошибка: {e}")
            return False
            
        print("  Тест 5: CachedAIAnalyzer")
        try:
            # Создаем новый кеш для теста
            test_cache = AnalysisCache(max_size=5)
            
            # Сохраняем результат в кеш
            test_cache.set("mock_ai_function_success", "Кешированный результат", {"test": "profile"})
            
            # Получаем результат из кеша
            cached_result = test_cache.get("mock_ai_function_success", {"test": "profile"})
            if cached_result == "Кешированный результат":
                print("    ✅ Кеширование работает корректно")
            else:
                print(f"    ❌ Кеширование не работает: {cached_result}")
                return False
        except Exception as e:
            print(f"    ❌ Ошибка в кешировании: {e}")
            return False
            
        print("  Тест 6: CachedAIAnalyzer.cached_analysis с успешным результатом")
        try:
            # Мокируем AI функцию
            mock_ai_func = AsyncMock(return_value="Результат AI")
            
            # Первый вызов - должен выполнить функцию
            result1 = await CachedAIAnalyzer.cached_analysis(mock_ai_func, {"test": "data"})
            
            # Второй вызов с теми же параметрами - должен использовать кеш
            result2 = await CachedAIAnalyzer.cached_analysis(mock_ai_func, {"test": "data"})
            
            # Проверяем, что функция была вызвана только один раз
            if mock_ai_func.call_count == 1 and result1 == result2 == "Результат AI":
                print("    ✅ Кешированный анализ работает корректно для успешных результатов")
            else:
                print(f"    ❌ Кеширование не работает: вызовы={mock_ai_func.call_count}, результат1={result1}, результат2={result2}")
                return False
        except Exception as e:
            print(f"    ❌ Ошибка в кешированном анализе: {e}")
            return False
            
        print("  Тест 7: CachedAIAnalyzer.cached_analysis с ошибкой не кешируется")
        try:
            # Создаем новый кеш для теста
            from helpers.ai_analyzer import analysis_cache
            original_cache = analysis_cache
            test_cache = AnalysisCache(max_size=5)
            # Заменяем глобальный кеш на тестовый
            import helpers.ai_analyzer
            helpers.ai_analyzer.analysis_cache = test_cache
            
            # Мокируем AI функцию, которая возвращает ошибку
            mock_ai_func_error = AsyncMock(return_value=M.ERRORS.AI_GENERIC)
            
            # Первый вызов - должен выполнить функцию
            result1 = await CachedAIAnalyzer.cached_analysis(mock_ai_func_error, {"test": "data"})
            
            # Второй вызов с теми же параметрами - должен снова выполнить функцию (ошибки не кешируются)
            result2 = await CachedAIAnalyzer.cached_analysis(mock_ai_func_error, {"test": "data"})
            
            # Восстанавливаем оригинальный кеш
            helpers.ai_analyzer.analysis_cache = original_cache
            
            # Проверяем, что функция была вызвана дважды (ошибки не кешируются)
            if mock_ai_func_error.call_count == 2 and result1 == result2 == M.ERRORS.AI_GENERIC:
                print("    ✅ Кешированный анализ корректно не кеширует ошибки")
            else:
                print(f"    ❌ Ошибки кешируются неправильно: вызовы={mock_ai_func_error.call_count}, результат1={result1}, результат2={result2}")
                return False
        except Exception as e:
            # Восстанавливаем оригинальный кеш в случае ошибки
            try:
                import helpers.ai_analyzer
                helpers.ai_analyzer.analysis_cache = original_cache
            except:
                pass
            print(f"    ❌ Ошибка в кешированном анализе с ошибкой: {e}")
            return False
            
        print("  Тест 8: AIAnalyzer с прогрессом")
        try:
            update = MockUpdate()
            update.effective_chat = Mock()
            update.effective_chat.id = 12345
            
            # Мокируем функции прогресса
            import helpers.progress
            original_action_typing = helpers.progress.action_typing
            original_progress_start = helpers.progress.Progress.start
            original_progress_animate = helpers.progress.Progress.animate
            
            helpers.progress.action_typing = AsyncMock()
            mock_progress = Mock()
            mock_progress.animate = AsyncMock()
            mock_progress.set = AsyncMock()
            mock_progress.finish = AsyncMock()
            helpers.progress.Progress.start = AsyncMock(return_value=mock_progress)
            
            # Мокируем AI функцию
            mock_ai_func = AsyncMock(return_value="Результат с прогрессом")
            
            result, progress = await AIAnalyzer.analysis_with_progress(
                update, mock_ai_func, {"test": "data"}
            )
            
            # Восстанавливаем оригинальные функции
            helpers.progress.action_typing = original_action_typing
            helpers.progress.Progress.start = original_progress_start
            helpers.progress.Progress.animate = original_progress_animate
            
            if result == "Результат с прогрессом":
                print("    ✅ Анализ с прогрессом выполнен корректно")
            else:
                print(f"    ❌ Неожиданный результат: {result}")
                return False
        except Exception as e:
            print(f"    ❌ Ошибка в анализе с прогрессом: {e}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Критическая ошибка в тесте: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Основная функция тестирования."""
    print("🚀 Тестирование совместимости AIAnalyzer")
    print("=" * 50)
    
    success = True
    
    try:
        success &= await test_ai_analyzer_compatibility()
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 Все тесты совместимости пройдены!")
            print("✅ AIAnalyzer полностью совместим с существующими AI функциями")
        else:
            print("💥 Некоторые тесты провалены!")
            print("❌ Нужно исправить несовместимости")
            
    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)