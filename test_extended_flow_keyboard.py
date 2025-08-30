#!/usr/bin/env python3
# test_extended_flow_keyboard.py
"""
Тест для проверки работы клавиатуры в extended_flow.py после изменений.
"""

import sys
import os

# Добавляем корень проекта в PATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_extended_flow_import():
    """Проверяем, что extended_flow.py импортируется без ошибок."""
    print("🔍 Тест импорта extended_flow.py...")
    
    try:
        # Пробуем импортировать модуль
        import flows.extended_flow
        print("✅ extended_flow.py импортируется успешно")
        return True
    except Exception as e:
        print(f"❌ Ошибка импорта extended_flow.py: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_keyboard_function():
    """Проверяем, что функция клавиатуры работает."""
    print("\n🔍 Тест функции клавиатуры...")
    
    try:
        # Импортируем функцию из flows.extended_flow
        # Для этого нужно импортировать модуль, который уже использует новую клавиатуру
        from flows.extended_flow import show_extended_only_profile
        print("✅ Функция show_extended_only_profile импортирована")
        
        # Проверяем, что можно импортировать новую клавиатуру
        from helpers.keyboards import build_after_analysis_keyboard
        keyboard = build_after_analysis_keyboard()
        print(f"✅ Новая клавиатура создана: {len(keyboard.keyboard)} рядов")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка при тестировании клавиатуры: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Основная функция тестирования."""
    print("🚀 Тестирование изменений в extended_flow.py")
    print("=" * 50)
    
    success = True
    
    try:
        success &= test_extended_flow_import()
        success &= test_keyboard_function()
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 Все тесты пройдены!")
            print("✅ Можно безопасно использовать extended_flow.py с новыми клавиатурами")
        else:
            print("💥 Некоторые тесты провалены!")
            print("❌ Нужно проверить изменения")
            
    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    return success

if __name__ == "__main__":
    result = main()
    exit(0 if result else 1)