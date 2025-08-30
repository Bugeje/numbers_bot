#!/usr/bin/env python3
# test_keyboard_integration.py
"""
Интеграционный тест для проверки работы клавиатур в боте.
Этот тест можно запустить без запуска всего бота.
"""

import sys
import os
import asyncio

# Добавляем корень проекта в PATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Мock объекты для тестирования
class MockUpdate:
    def __init__(self):
        self.effective_message = MockMessage()
        self.effective_chat = MockChat()

class MockMessage:
    def __init__(self):
        self.message_id = 12345
    
    async def reply_text(self, text, **kwargs):
        print(f"📤 Отправка сообщения: {text[:50]}...")
        if 'reply_markup' in kwargs:
            keyboard = kwargs['reply_markup']
            print(f"   С клавиатурой: {len(keyboard.keyboard)} рядов")
        return MockMessage()

class MockChat:
    def __init__(self):
        self.id = 98765

class MockContext:
    def __init__(self):
        self.user_data = {
            "name": "Тест Пользователь",
            "birthdate": "01.01.1990",
            "core_profile": {
                "life_path": "1",
                "birthday": "1",
                "expression": "2",
                "soul": "3", 
                "personality": "4"
            }
        }

async def test_keyboard_creation():
    """Тест создания клавиатур через новые компоненты."""
    print("🧪 Тест создания клавиатур...")
    
    try:
        # Импортируем новые компоненты
        from helpers.keyboards import StandardKeyboards, KeyboardBuilder, KeyboardUtils
        from interface.menus import build_after_analysis_keyboard as old_keyboard
        
        # Создаем клавиатуры разными способами
        print("\n1. Создание через StandardKeyboards:")
        new_kb = StandardKeyboards.after_analysis_keyboard()
        print(f"   ✅ Создана клавиатура с {len(new_kb.keyboard)} рядами")
        
        print("\n2. Создание через KeyboardBuilder:")
        custom_kb = KeyboardBuilder.create_reply_keyboard([
            ["Тест 1", "Тест 2"],
            ["Тест 3"]
        ])
        print(f"   ✅ Создана кастомная клавиатура с {len(custom_kb.keyboard)} рядами")
        
        print("\n3. Создание через KeyboardUtils:")
        grid_kb = KeyboardUtils.create_grid_keyboard(["A", "B", "C", "D"], columns=2)
        print(f"   ✅ Создана сетка клавиатура с {len(grid_kb.keyboard)} рядами")
        
        print("\n4. Сравнение с оригинальной клавиатурой:")
        old_kb = old_keyboard()
        print(f"   ✅ Оригинальная клавиатура с {len(old_kb.keyboard)} рядами")
        
        # Проверяем совместимость
        old_structure = [[btn.text for btn in row] for row in old_kb.keyboard]
        new_structure = [[btn.text for btn in row] for row in new_kb.keyboard]
        
        if old_structure == new_structure:
            print("   ✅ Структуры полностью совпадают!")
        else:
            print("   ❌ Структуры различаются!")
            print(f"   Оригинал: {old_structure}")
            print(f"   Новая: {new_structure}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при создании клавиатур: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_keyboard_usage():
    """Тест использования клавиатур в сообщениях."""
    print("\n🧪 Тест использования клавиатур в сообщениях...")
    
    try:
        from helpers.keyboards import StandardKeyboards
        from helpers.messages import M
        
        # Создаем mock объекты
        update = MockUpdate()
        context = MockContext()
        
        # Создаем клавиатуру
        keyboard = StandardKeyboards.after_analysis_keyboard()
        
        # Имитируем отправку сообщения с клавиатурой
        message_text = M.HINTS.NEXT_STEP
        print(f"📤 Имитация отправки: '{message_text}'")
        print(f"   С клавиатурой: {len(keyboard.keyboard)} рядов")
        
        # Проверяем структуру клавиатуры
        for i, row in enumerate(keyboard.keyboard):
            buttons = [btn.text for btn in row]
            print(f"   Ряд {i+1}: {buttons}")
        
        print("   ✅ Сообщение с клавиатурой отправлено успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при использовании клавиатуры: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_keyboard_aliases():
    """Тест алиасов для обратной совместимости."""
    print("\n🧪 Тест алиасов клавиатур...")
    
    try:
        # Тест алиаса для build_after_analysis_keyboard
        from helpers.keyboards import build_after_analysis_keyboard as new_alias
        from interface.menus import build_after_analysis_keyboard as old_function
        
        new_kb = new_alias()
        old_kb = old_function()
        
        new_structure = [[btn.text for btn in row] for row in new_kb.keyboard]
        old_structure = [[btn.text for btn in row] for row in old_kb.keyboard]
        
        if new_structure == old_structure:
            print("   ✅ Алиас работает корректно!")
            return True
        else:
            print("   ❌ Алиас работает некорректно!")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка в алиасах: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Основная функция тестирования."""
    print("🚀 Запуск интеграционных тестов клавиатур")
    print("=" * 50)
    
    success = True
    
    try:
        # Запускаем все тесты
        success &= await test_keyboard_creation()
        success &= await test_keyboard_usage()
        success &= await test_keyboard_aliases()
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 ВСЕ ИНТЕГРАЦИОННЫЕ ТЕСТЫ ПРОЙДЕНЫ!")
            print("✅ Можно безопасно начинать внедрение новых клавиатур")
        else:
            print("💥 НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ!")
            print("❌ Нужно исправить проблемы перед внедрением")
            
    except Exception as e:
        print(f"💥 КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    return success


if __name__ == "__main__":
    # Запускаем асинхронный тест
    result = asyncio.run(main())
    exit(0 if result else 1)