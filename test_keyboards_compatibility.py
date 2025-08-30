# test_keyboards_compatibility.py
"""
Тест совместимости клавиатур - проверяет, что новые KeyboardBuilder
создают точно такие же клавиатуры, как и старые функции.
"""

import sys
import os

# Добавляем корень проекта в PATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_keyboard_compatibility():
    """Проверяем совместимость старых и новых клавиатур."""
    print("🧪 Тестирование совместимости клавиатур...")
    
    # Импортируем старую реализацию
    from interface.menus import build_after_analysis_keyboard as old_keyboard
    
    # Импортируем новую реализацию
    from helpers.keyboards import StandardKeyboards
    
    # Создаем клавиатуры
    old_kb = old_keyboard()
    new_kb = StandardKeyboards.after_analysis_keyboard()
    
    # Сравниваем структуру
    print(f"Старая клавиатура: {len(old_kb.keyboard)} рядов")
    print(f"Новая клавиатура: {len(new_kb.keyboard)} рядов")
    
    # Проверяем каждый ряд
    if len(old_kb.keyboard) != len(new_kb.keyboard):
        print("❌ Количество рядов не совпадает!")
        return False
    
    for i, (old_row, new_row) in enumerate(zip(old_kb.keyboard, new_kb.keyboard)):
        print(f"\nРяд {i+1}:")
        old_texts = [btn.text for btn in old_row]
        new_texts = [btn.text for btn in new_row]
        
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
    
    print("\n✅ Все проверки пройдены! Клавиатуры полностью совместимы.")
    return True


def test_alias_compatibility():
    """Проверяем, что алиас работает корректно."""
    print("\n🧪 Тестирование алиаса...")
    
    # Импортируем алиас из новой системы
    from helpers.keyboards import build_after_analysis_keyboard as alias_keyboard
    
    # Импортируем старую реализацию
    from interface.menus import build_after_analysis_keyboard as old_keyboard
    
    old_kb = old_keyboard()
    alias_kb = alias_keyboard()
    
    # Сравниваем
    old_structure = [[btn.text for btn in row] for row in old_kb.keyboard]
    alias_structure = [[btn.text for btn in row] for row in alias_kb.keyboard]
    
    if old_structure == alias_structure:
        print("✅ Алиас работает корректно!")
        return True
    else:
        print("❌ Алиас работает некорректно!")
        print(f"Старый: {old_structure}")
        print(f"Алиас: {alias_structure}")
        return False


if __name__ == "__main__":
    print("🚀 Запуск тестов совместимости клавиатур")
    print("=" * 50)
    
    success = True
    
    try:
        success = test_keyboard_compatibility() and success
        success = test_alias_compatibility() and success
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Можно внедрять новые клавиатуры.")
        else:
            print("💥 ТЕСТЫ НЕ ПРОЙДЕНЫ! Нужно исправить несовместимости.")
            
    except Exception as e:
        print(f"💥 ОШИБКА ПРИ ТЕСТИРОВАНИИ: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    exit(0 if success else 1)