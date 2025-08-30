# test_keyboards_simple.py
"""
Упрощенный тест совместимости клавиатур - проверяет структуру клавиатур без импорта Telegram.
"""

import sys
import os

# Добавляем корень проекта в PATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def create_mock_btn(text):
    """Создаем мок кнопки для тестирования."""
    class MockButton:
        def __init__(self, text):
            self.text = text
    return MockButton(text)


def create_mock_keyboard(buttons, resize_keyboard=True):
    """Создаем мок клавиатуры для тестирования."""
    class MockKeyboard:
        def __init__(self, keyboard, resize_keyboard=True):
            self.keyboard = keyboard
            self.resize_keyboard = resize_keyboard
    return MockKeyboard(buttons, resize_keyboard)


def test_old_keyboard_structure():
    """Тестируем структуру старой клавиатуры."""
    # Это копия структуры из interface/menus.py
    buttons = [
        [create_mock_btn(" CORE "), create_mock_btn(" PARTNER ")],
        [create_mock_btn(" EXTENDED "), create_mock_btn(" BRIDGES ")],
        [create_mock_btn(" CYCLES "), create_mock_btn(" MONTHS ")],
        [create_mock_btn(" CALENDAR_DAYS ")],
        [create_mock_btn(" RESTART ")]
    ]
    return create_mock_keyboard(buttons)


def test_new_keyboard_structure():
    """Тестируем структуру новой клавиатуры."""
    # Имитируем логику StandardKeyboards.after_analysis_keyboard()
    buttons_data = [
        [" CORE ", " PARTNER "],
        [" EXTENDED ", " BRIDGES "],
        [" CYCLES ", " MONTHS "],
        [" CALENDAR_DAYS "],
        [" RESTART "]
    ]
    
    # Создаем кнопки как это делает KeyboardBuilder
    buttons = []
    for row_data in buttons_data:
        row = [create_mock_btn(text) for text in row_data]
        buttons.append(row)
    
    return create_mock_keyboard(buttons)


def compare_keyboards(old_kb, new_kb):
    """Сравниваем две клавиатуры."""
    print("🔍 Сравнение структуры клавиатур...")
    
    # Проверяем количество рядов
    if len(old_kb.keyboard) != len(new_kb.keyboard):
        print(f"❌ Разное количество рядов: {len(old_kb.keyboard)} vs {len(new_kb.keyboard)}")
        return False
    
    print(f"✅ Одинаковое количество рядов: {len(old_kb.keyboard)}")
    
    # Проверяем каждый ряд
    for i, (old_row, new_row) in enumerate(zip(old_kb.keyboard, new_kb.keyboard)):
        old_texts = [btn.text.strip() for btn in old_row]
        new_texts = [btn.text.strip() for btn in new_row]
        
        print(f"Ряд {i+1}:")
        print(f"  Старый: {old_texts}")
        print(f"  Новый:  {new_texts}")
        
        if old_texts != new_texts:
            print(f"  ❌ Ряд {i+1} не совпадает!")
            return False
        else:
            print(f"  ✅ Ряд {i+1} идентичен")
    
    # Проверяем настройки
    if old_kb.resize_keyboard != new_kb.resize_keyboard:
        print(f"❌ resize_keyboard не совпадает: {old_kb.resize_keyboard} vs {new_kb.resize_keyboard}")
        return False
    
    print("✅ Все настройки совпадают")
    return True


def test_keyboard_builder_logic():
    """Тестируем логику KeyboardBuilder.create_reply_keyboard."""
    print("\n🧪 Тестирование логики KeyboardBuilder...")
    
    # Тестируем создание простой клавиатуры
    from helpers.keyboards import KeyboardBuilder
    
    # Тест 1: Одиночные кнопки
    buttons1 = ["Кнопка 1", "Кнопка 2", "Кнопка 3"]
    kb1 = KeyboardBuilder.create_reply_keyboard(buttons1)
    
    expected1 = [["Кнопка 1"], ["Кнопка 2"], ["Кнопка 3"]]
    actual1 = [[btn.text for btn in row] for row in kb1.keyboard]
    
    print(f"Тест 1 - Одиночные кнопки:")
    print(f"  Ожидаем: {expected1}")
    print(f"  Получили: {actual1}")
    
    if expected1 == actual1:
        print("  ✅ Тест 1 пройден")
    else:
        print("  ❌ Тест 1 провален")
        return False
    
    # Тест 2: Ряды кнопок
    buttons2 = [["Кнопка 1", "Кнопка 2"], ["Кнопка 3", "Кнопка 4"]]
    kb2 = KeyboardBuilder.create_reply_keyboard(buttons2)
    
    expected2 = [["Кнопка 1", "Кнопка 2"], ["Кнопка 3", "Кнопка 4"]]
    actual2 = [[btn.text for btn in row] for row in kb2.keyboard]
    
    print(f"Тест 2 - Ряды кнопок:")
    print(f"  Ожидаем: {expected2}")
    print(f"  Получили: {actual2}")
    
    if expected2 == actual2:
        print("  ✅ Тест 2 пройден")
    else:
        print("  ❌ Тест 2 провален")
        return False
    
    return True


def main():
    """Основная функция тестирования."""
    print("🚀 Запуск упрощенных тестов совместимости клавиатур")
    print("=" * 60)
    
    success = True
    
    try:
        # Тест 1: Сравнение структуры клавиатур
        print("Тест 1: Сравнение структуры клавиатур")
        old_kb = test_old_keyboard_structure()
        new_kb = test_new_keyboard_structure()
        
        if compare_keyboards(old_kb, new_kb):
            print("✅ Тест 1 пройден - структуры идентичны!")
        else:
            print("❌ Тест 1 провален - структуры различаются!")
            success = False
        
        print("\n" + "-" * 60)
        
        # Тест 2: Логика KeyboardBuilder
        if test_keyboard_builder_logic():
            print("✅ Тест 2 пройден - логика KeyboardBuilder работает корректно!")
        else:
            print("❌ Тест 2 провален - проблемы с KeyboardBuilder!")
            success = False
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
            print("✅ Можно безопасно внедрять новые клавиатуры")
        else:
            print("💥 НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ!")
            print("❌ Нужно исправить проблемы перед внедрением")
            
    except Exception as e:
        print(f"💥 ОШИБКА ПРИ ТЕСТИРОВАНИИ: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    return success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)