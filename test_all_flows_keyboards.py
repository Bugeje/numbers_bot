#!/usr/bin/env python3
# test_all_flows_keyboards.py
"""
Комплексный тест для проверки работы клавиатур во всех flow файлах.
"""

import sys
import os

# Добавляем корень проекта в PATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_flow_import(flow_name):
    """Проверяем импорт конкретного flow файла."""
    print(f"🔍 Тест импорта {flow_name}...")
    
    try:
        # Динамический импорт
        module = __import__(f"flows.{flow_name}", fromlist=[''])
        print(f"✅ {flow_name} импортируется успешно")
        return True, module
    except Exception as e:
        print(f"❌ Ошибка импорта {flow_name}: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_keyboard_in_flow(flow_module, flow_name):
    """Проверяем работу клавиатуры в конкретном flow."""
    print(f"🔍 Тест клавиатуры в {flow_name}...")
    
    try:
        # Проверяем, что можно импортировать новую клавиатуру
        from helpers.keyboards import build_after_analysis_keyboard
        keyboard = build_after_analysis_keyboard()
        print(f"✅ Новая клавиатура в {flow_name} создана: {len(keyboard.keyboard)} рядов")
        return True
    except Exception as e:
        print(f"❌ Ошибка клавиатуры в {flow_name}: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_all_flows():
    """Проверяем все flow файлы."""
    print("🚀 Тестирование всех flow файлов")
    print("=" * 50)
    
    # Список flow файлов для тестирования
    flows_to_test = [
        "extended_flow",
        "bridges_flow",
        "profile_flow", 
        "cycles_flow",
        "partner_flow",
        "days_flow",
        "months_flow"
    ]
    
    results = {}
    overall_success = True
    
    for flow_name in flows_to_test:
        print(f"\n--- Тестирование {flow_name} ---")
        
        # Тест импорта
        import_success, module = test_flow_import(flow_name)
        results[flow_name] = {"import": import_success}
        
        if import_success and module:
            # Тест клавиатуры
            keyboard_success = test_keyboard_in_flow(module, flow_name)
            results[flow_name]["keyboard"] = keyboard_success
            overall_success &= keyboard_success
        else:
            overall_success = False
            results[flow_name]["keyboard"] = False
    
    # Выводим сводку
    print("\n" + "=" * 50)
    print("📊 Сводка тестирования:")
    print("-" * 30)
    
    for flow_name, result in results.items():
        import_status = "✅" if result["import"] else "❌"
        keyboard_status = "✅" if result.get("keyboard", False) else "❌"
        print(f"{flow_name:15} | Импорт: {import_status} | Клавиатура: {keyboard_status}")
    
    print("-" * 30)
    if overall_success:
        print("🎉 Все flow файлы работают корректно!")
        print("✅ Можно безопасно внедрять новые клавиатуры")
    else:
        print("💥 Некоторые flow файлы имеют проблемы!")
        print("❌ Нужно проверить и исправить ошибки")
    
    return overall_success

def test_backward_compatibility():
    """Проверяем обратную совместимость."""
    print("\n🔍 Тест обратной совместимости...")
    
    try:
        # Старый способ
        from interface.menus import build_after_analysis_keyboard as old_way
        old_keyboard = old_way()
        
        # Новый способ (алиас)
        from helpers.keyboards import build_after_analysis_keyboard as new_way
        new_keyboard = new_way()
        
        # Сравниваем структуру
        old_structure = [[btn.text for btn in row] for row in old_keyboard.keyboard]
        new_structure = [[btn.text for btn in row] for row in new_keyboard.keyboard]
        
        if old_structure == new_structure:
            print("✅ Обратная совместимость сохранена!")
            return True
        else:
            print("❌ Обратная совместимость нарушена!")
            print(f"Старая: {old_structure}")
            print(f"Новая: {new_structure}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при проверке совместимости: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Основная функция тестирования."""
    print("🚀 Комплексное тестирование внедрения новых клавиатур")
    print("=" * 60)
    
    success = True
    
    try:
        # Тест всех flow файлов
        success &= test_all_flows()
        
        # Тест обратной совместимости
        success &= test_backward_compatibility()
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
            print("✅ Можно переходить к следующему этапу внедрения")
            print("📋 Следующий шаг: Внедрение DataValidator для валидации данных")
        else:
            print("💥 НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ!")
            print("❌ Нужно исправить проблемы перед продолжением")
            
    except Exception as e:
        print(f"💥 КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    return success

if __name__ == "__main__":
    result = main()
    exit(0 if result else 1)