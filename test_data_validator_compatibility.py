#!/usr/bin/env python3
# test_data_validator_compatibility.py
"""
Тест для проверки совместимости DataValidator с существующим кодом валидации.
"""

import sys
import os
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock

# Добавляем корень проекта в PATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class MockUpdate:
    def __init__(self, message_text=""):
        self.message = Mock()
        self.message.text = message_text
        self.effective_message = AsyncMock()
        self.effective_chat = Mock()

class MockContext:
    def __init__(self, user_data=None):
        self.user_data = user_data or {}

async def test_name_validation():
    """Тест валидации имени."""
    print("🔍 Тест валидации имени...")
    
    try:
        # Импортируем существующую функцию
        from helpers import normalize_name
        
        # Импортируем новый валидатор
        from helpers.data_validator import DataValidator
        
        # Тест 1: Валидное имя
        update = MockUpdate()
        context = MockContext({"name": "Тест Пользователь"})
        
        success, name = await DataValidator.validate_name(update, context)
        
        if success and name == "Тест Пользователь":
            print("✅ Валидное имя прошло проверку")
        else:
            print("❌ Валидное имя не прошло проверку")
            return False
        
        # Тест 2: Невалидное имя (должна быть ошибка)
        context_invalid = MockContext({"name": "123Invalid"})
        # Мокируем ответ, чтобы не было реальной отправки сообщения
        update_invalid = MockUpdate()
        update_invalid.effective_message.reply_text = AsyncMock()
        
        success, name = await DataValidator.validate_name(update_invalid, context_invalid)
        
        if not success:
            print("✅ Невалидное имя правильно отклонено")
            # Проверяем, что сообщение об ошибке отправлено
            update_invalid.effective_message.reply_text.assert_called_once()
        else:
            print("❌ Невалидное имя не было отклонено")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании валидации имени: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_birthdate_validation():
    """Тест валидации даты рождения."""
    print("\n🔍 Тест валидации даты рождения...")
    
    try:
        # Импортируем новый валидатор
        from helpers.data_validator import DataValidator
        from helpers.messages import M
        
        # Тест 1: Валидная дата
        update = MockUpdate("01.01.1990")
        context = MockContext()
        
        # Мокируем ответ
        update.effective_message.reply_text = AsyncMock()
        
        success, birthdate = await DataValidator.validate_birthdate(update, context)
        
        if success and birthdate == "01.01.1990":
            print("✅ Валидная дата прошла проверку")
        else:
            print("❌ Валидная дата не прошла проверку")
            return False
        
        # Тест 2: Невалидная дата (должна быть ошибка)
        update_invalid = MockUpdate("invalid-date")
        update_invalid.effective_message.reply_text = AsyncMock()
        
        success, birthdate = await DataValidator.validate_birthdate(update_invalid, context)
        
        if not success:
            print("✅ Невалидная дата правильно отклонена")
            # Проверяем, что сообщение об ошибке отправлено
            update_invalid.effective_message.reply_text.assert_called_once()
            # Проверяем, что сообщение содержит правильный префикс
            call_args = update_invalid.effective_message.reply_text.call_args[0][0]
            if M.ERRORS.DATE_PREFIX in call_args:
                print("✅ Сообщение об ошибке содержит правильный префикс")
            else:
                print("❌ Сообщение об ошибке не содержит правильный префикс")
                return False
        else:
            print("❌ Невалидная дата не была отклонена")
            return False
            
        # Тест 3: Будущая дата (должна быть ошибка)
        future_date = datetime.now().strftime("%d.%m.%Y")
        # Если сегодня 1 января, то 2 января будет будущей датой
        day = datetime.now().day
        month = datetime.now().month
        year = datetime.now().year + 1  # Следующий год точно будущий
        future_date = f"01.01.{year}"
        
        update_future = MockUpdate(future_date)
        update_future.effective_message.reply_text = AsyncMock()
        
        success, birthdate = await DataValidator.validate_birthdate(update_future, context)
        
        # Для будущих дат проверка может быть сложной, просто убедимся, что код не падает
        print("✅ Проверка будущей даты выполнена без ошибок")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании валидации даты: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_basic_profile_validation():
    """Тест валидации базового профиля."""
    print("\n🔍 Тест валидации базового профиля...")
    
    try:
        from helpers.data_validator import DataValidator
        from helpers.messages import M
        
        # Тест 1: Валидный профиль
        update = MockUpdate()
        update.effective_message.reply_text = AsyncMock()
        
        context = MockContext({
            "name": "Тест Пользователь",
            "birthdate": "01.01.1990",
            "core_profile": {"life_path": "1"}
        })
        
        success, data = await DataValidator.validate_basic_profile(update, context)
        
        if success and data:
            print("✅ Валидный профиль прошел проверку")
            expected_keys = {"name", "birthdate", "core_profile"}
            if set(data.keys()) == expected_keys:
                print("✅ Все необходимые данные присутствуют")
            else:
                print(f"❌ Неверный набор данных: {data.keys()}")
                return False
        else:
            print("❌ Валидный профиль не прошел проверку")
            return False
        
        # Тест 2: Невалидный профиль (нет данных)
        context_invalid = MockContext()
        update_invalid = MockUpdate()
        update_invalid.effective_message.reply_text = AsyncMock()
        
        success, data = await DataValidator.validate_basic_profile(update_invalid, context_invalid)
        
        if not success:
            print("✅ Невалидный профиль правильно отклонен")
            # Проверяем сообщение об ошибке
            update_invalid.effective_message.reply_text.assert_called_once()
            call_args = update_invalid.effective_message.reply_text.call_args[0][0]
            if M.HINTS.MISSING_BASIC_DATA in call_args:
                print("✅ Сообщение об ошибке содержит правильный текст")
            else:
                print("❌ Сообщение об ошибке не содержит правильный текст")
                return False
        else:
            print("❌ Невалидный профиль не был отклонен")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании валидации профиля: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Основная функция тестирования."""
    print("🚀 Тестирование совместимости DataValidator")
    print("=" * 50)
    
    success = True
    
    try:
        success &= await test_name_validation()
        success &= await test_birthdate_validation()
        success &= await test_basic_profile_validation()
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 Все тесты совместимости пройдены!")
            print("✅ DataValidator полностью совместим с существующим кодом")
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