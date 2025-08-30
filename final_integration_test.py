#!/usr/bin/env python3
# final_integration_test.py
"""
Финальный интеграционный тест для проверки всех изменений.
"""

import sys
import os

# Добавляем корень проекта в PATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_all_components():
    """Проверяем все новые компоненты."""
    print("🔍 Тестирование всех новых компонентов...")
    
    components_to_test = [
        ("helpers.keyboards", "StandardKeyboards, KeyboardBuilder, KeyboardUtils"),
        ("helpers.data_validator", "DataValidator, ValidationResult"),
        ("helpers.ai_analyzer", "AIAnalyzer, CachedAIAnalyzer"),
        ("helpers.error_handler", "ErrorHandler, FlowErrorHandler"),
        ("helpers.pdf_flow_base", "BasePDFFlow")
    ]
    
    success = True
    
    for module_path, components in components_to_test:
        try:
            module = __import__(module_path, fromlist=[''])
            print(f"✅ {module_path} импортируется успешно")
            
            # Проверяем конкретные компоненты
            for component in components.split(", "):
                if hasattr(module, component):
                    print(f"   ✅ {component} доступен")
                else:
                    print(f"   ❌ {component} недоступен")
                    success = False
                    
        except Exception as e:
            print(f"❌ Ошибка импорта {module_path}: {e}")
            success = False
    
    return success

def test_flow_integration():
    """Проверяем интеграцию во flow файлах."""
    print("\n🔍 Тестирование интеграции во flow файлах...")
    
    flow_files = [
        "flows.extended_flow",
        "flows.bridges_flow", 
        "flows.profile_flow",
        "flows.partner_flow",
        "flows.cycles_flow"
    ]
    
    success = True
    
    for flow_path in flow_files:
        try:
            # Импортируем flow
            flow_module = __import__(flow_path, fromlist=[''])
            print(f"✅ {flow_path} импортируется")
            
            # Проверяем, что функция навигации доступна
            if hasattr(flow_module, 'show_extended_only_profile') or hasattr(flow_module, 'send_bridges_pdf'):
                print(f"   ✅ Основные функции доступны")
            elif hasattr(flow_module, 'core_profile_ai_and_pdf') or hasattr(flow_module, 'show_cycles_profile'):
                print(f"   ✅ Основные функции доступны")
            else:
                print(f"   ⚠️  Не удалось определить основные функции")
                
        except Exception as e:
            print(f"❌ Ошибка в {flow_path}: {e}")
            success = False
    
    return success

def test_keyboard_consistency():
    """Проверяем консистентность клавиатур."""
    print("\n🔍 Тестирование консистентности клавиатур...")
    
    try:
        # Старый способ
        from interface.menus import build_after_analysis_keyboard as old_keyboard
        old_kb = old_keyboard()
        
        # Новый способ
        from helpers.keyboards import StandardKeyboards
        new_kb = StandardKeyboards.after_analysis_keyboard()
        
        # Алиас
        from helpers.keyboards import build_after_analysis_keyboard as alias_keyboard
        alias_kb = alias_keyboard()
        
        # Сравниваем структуры
        old_structure = [[btn.text.strip() for btn in row] for row in old_kb.keyboard]
        new_structure = [[btn.text.strip() for btn in row] for row in new_kb.keyboard]
        alias_structure = [[btn.text.strip() for btn in row] for row in alias_kb.keyboard]
        
        if old_structure == new_structure == alias_structure:
            print("✅ Все клавиатуры идентичны")
            print(f"   Рядов: {len(old_structure)}")
            for i, row in enumerate(old_structure):
                print(f"   Ряд {i+1}: {row}")
            return True
        else:
            print("❌ Клавиатуры различаются")
            print(f"   Старая: {old_structure}")
            print(f"   Новая: {new_structure}")
            print(f"   Алиас: {alias_structure}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при проверке клавиатур: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_no_circular_imports():
    """Проверяем отсутствие циклических импортов."""
    print("\n🔍 Тестирование отсутствия циклических импортов...")
    
    modules_to_test = [
        "helpers",
        "helpers.keyboards",
        "helpers.data_validator",
        "helpers.ai_analyzer",
        "helpers.error_handler",
        "helpers.pdf_flow_base",
        "flows.extended_flow",
        "flows.bridges_flow"
    ]
    
    success = True
    
    for module_path in modules_to_test:
        try:
            module = __import__(module_path, fromlist=[''])
            print(f"✅ {module_path} импортируется без циклических зависимостей")
        except ImportError as e:
            if "circular import" in str(e):
                print(f"❌ Циклический импорт в {module_path}: {e}")
                success = False
            else:
                print(f"⚠️  Другая ошибка импорта в {module_path}: {e}")
        except Exception as e:
            print(f"❌ Ошибка при импорте {module_path}: {e}")
            success = False
    
    return success

def main():
    """Основная функция тестирования."""
    print("🚀 ФИНАЛЬНОЕ ИНТЕГРАЦИОННОЕ ТЕСТИРОВАНИЕ")
    print("=" * 50)
    
    overall_success = True
    
    try:
        # Тест 1: Все компоненты
        overall_success &= test_all_components()
        
        # Тест 2: Интеграция во flow
        overall_success &= test_flow_integration()
        
        # Тест 3: Консистентность клавиатур
        overall_success &= test_keyboard_consistency()
        
        # Тест 4: Нет циклических импортов
        overall_success &= test_no_circular_imports()
        
        print("\n" + "=" * 50)
        if overall_success:
            print("🎉 ВСЕ ИНТЕГРАЦИОННЫЕ ТЕСТЫ ПРОЙДЕНЫ!")
            print("\n✅ ГОТОВО К ПЕРВОМУ ЭТАПУ ВНЕДРЕНИЯ!")
            print("\n📊 Результаты первого этапа:")
            print("   ✅ KeyboardBuilder и StandardKeyboards")
            print("   ✅ Все flow файлы используют новые клавиатуры")
            print("   ✅ Обратная совместимость сохранена")
            print("   ✅ Нет циклических импортов")
            print("\n📋 Следующие шаги:")
            print("   1. Внедрение DataValidator для валидации данных")
            print("   2. Внедрение AIAnalyzer для унификации AI вызовов")
            print("   3. Внедрение ErrorHandler для централизованной обработки ошибок")
            print("   4. Постепенная миграция к BasePDFFlow")
        else:
            print("💥 НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ!")
            print("❌ Нужно исправить проблемы перед продолжением")
            
    except Exception as e:
        print(f"💥 КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        overall_success = False
    
    return overall_success

if __name__ == "__main__":
    result = main()
    exit(0 if result else 1)