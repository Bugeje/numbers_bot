#!/usr/bin/env python3
# test_bridges_flow_ai_integration.py
"""
Тест для проверки интеграции AIAnalyzer с bridges_flow.
"""

import sys
import os
import asyncio
from unittest.mock import Mock, AsyncMock

# Добавляем корень проекта в PATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class MockUpdate:
    def __init__(self):
        self.effective_message = AsyncMock()
        self.effective_chat = Mock()
        self.effective_chat.id = 12345

class MockContext:
    def __init__(self, user_data=None):
        self.user_data = user_data or {}

async def test_bridges_flow_ai_integration():
    """Тест интеграции AIAnalyzer с bridges_flow."""
    print("🔍 Тест интеграции AIAnalyzer с bridges_flow...")
    
    try:
        # Импортируем bridges_flow
        from flows.bridges_flow import send_bridges_pdf
        from intelligence import get_bridges_analysis
        
        # Создаем тестовые данные
        update = MockUpdate()
        context = MockContext({
            "name": "Тест Пользователь",
            "birthdate": "01.01.1990",
            "core_profile": {
                "life_path": "1",
                "birthday": "1",
                "expression": "2",
                "soul": "3",
                "personality": "4"
            },
            "extended_profile": {
                "maturity": "5",
                "rational_thought": "6",
                "imagination": "7",
                "career": "8",
                "inner_dreams": "9",
                "outer_dreams": "1",
                "illness": "2",
                "talent": "3"
            }
        })
        
        # Мокируем функции прогресса
        import helpers.progress
        original_action_typing = helpers.progress.action_typing
        original_action_upload = helpers.progress.action_upload
        original_progress_start = helpers.progress.Progress.start
        original_progress_animate = helpers.progress.Progress.animate
        original_progress_set = helpers.progress.Progress.set
        original_progress_finish = helpers.progress.Progress.finish
        
        helpers.progress.action_typing = AsyncMock()
        helpers.progress.action_upload = AsyncMock()
        mock_progress = Mock()
        mock_progress.animate = AsyncMock()
        mock_progress.set = AsyncMock()
        mock_progress.finish = AsyncMock()
        helpers.progress.Progress.start = AsyncMock(return_value=mock_progress)
        
        # Мокируем MessageManager
        import helpers
        original_message_manager = helpers.MessageManager
        helpers.MessageManager = Mock()
        helpers.MessageManager.return_value.cleanup_tracked_messages = AsyncMock()
        helpers.MessageManager.return_value.send_navigation_message = AsyncMock()
        
        # Мокируем AI функцию
        import intelligence.analysis
        original_get_bridges_analysis = intelligence.analysis.get_bridges_analysis
        intelligence.analysis.get_bridges_analysis = AsyncMock(return_value="Анализ мостов")
        
        # Мокируем PDF генерацию
        import output
        original_generate_bridges_pdf = output.generate_bridges_pdf
        output.generate_bridges_pdf = Mock()
        
        # Мокируем tempfile
        import tempfile
        original_tempfile = tempfile.NamedTemporaryFile
        tempfile.NamedTemporaryFile = Mock()
        tempfile.NamedTemporaryFile.return_value.__enter__ = Mock(return_value=Mock())
        tempfile.NamedTemporaryFile.return_value.__exit__ = Mock(return_value=None)
        tempfile.NamedTemporaryFile.return_value.name = "/tmp/test.pdf"
        
        # Мокируем open и os.unlink
        import builtins
        original_open = builtins.open
        builtins.open = Mock()
        mock_file = Mock()
        builtins.open.return_value.__enter__ = Mock(return_value=mock_file)
        builtins.open.return_value.__exit__ = Mock(return_value=None)
        
        import os
        original_os_unlink = os.unlink
        os.unlink = Mock()
        
        try:
            # Выполняем тест
            result = await send_bridges_pdf(update, context)
            
            # Проверяем результат
            if result == -1:  # ConversationHandler.END
                print("    ✅ Bridges flow успешно выполнен")
            else:
                print(f"    ❌ Неожиданный результат: {result}")
                return False
                
            # Проверяем, что AI функция была вызвана
            if intelligence.analysis.get_bridges_analysis.call_count > 0:
                print("    ✅ AI анализ мостов выполнен")
            else:
                print("    ❌ AI анализ мостов не был выполнен")
                return False
                
        finally:
            # Восстанавливаем оригинальные функции
            helpers.progress.action_typing = original_action_typing
            helpers.progress.action_upload = original_action_upload
            helpers.progress.Progress.start = original_progress_start
            helpers.progress.Progress.animate = original_progress_animate
            helpers.progress.Progress.set = original_progress_set
            helpers.progress.Progress.finish = original_progress_finish
            
            helpers.MessageManager = original_message_manager
            
            intelligence.analysis.get_bridges_analysis = original_get_bridges_analysis
            output.generate_bridges_pdf = original_generate_bridges_pdf
            tempfile.NamedTemporaryFile = original_tempfile
            builtins.open = original_open
            os.unlink = original_os_unlink
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в тесте: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Основная функция тестирования."""
    print("🚀 Тестирование интеграции AIAnalyzer с bridges_flow")
    print("=" * 50)
    
    success = True
    
    try:
        success &= await test_bridges_flow_ai_integration()
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 Тест интеграции пройден!")
            print("✅ Bridges flow успешно интегрирован с AIAnalyzer")
        else:
            print("💥 Тест интеграции провален!")
            print("❌ Нужно исправить интеграцию")
            
    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)