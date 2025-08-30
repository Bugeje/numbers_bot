#!/usr/bin/env python3
# test_profile_flow_validation.py
"""
Test to verify DataValidator integration with profile_flow validation.
"""

import sys
import os
import asyncio
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

async def test_profile_flow_validation_replacement():
    """Test replacing profile_flow validation with DataValidator."""
    print("🔍 Testing profile_flow validation replacement...")
    
    try:
        # Import existing validation functions
        from helpers import normalize_name, parse_and_normalize
        from helpers.messages import M
        
        # Import new DataValidator
        from helpers.data_validator import DataValidator
        
        # Test 1: Validate name using existing function
        print("  Testing existing name validation...")
        try:
            name = normalize_name("Тест Пользователь")
            print(f"    ✅ Existing name validation: {name}")
        except Exception as e:
            print(f"    ❌ Existing name validation failed: {e}")
            return False
        
        # Test 2: Validate name using DataValidator
        print("  Testing DataValidator name validation...")
        update = MockUpdate()
        context = MockContext({"name": "Тест Пользователь"})
        update.effective_message.reply_text = AsyncMock()
        
        success, validated_name = await DataValidator.validate_name(update, context)
        
        if success and validated_name == "Тест Пользователь":
            print(f"    ✅ DataValidator name validation: {validated_name}")
        else:
            print(f"    ❌ DataValidator name validation failed: success={success}, name={validated_name}")
            return False
        
        # Test 3: Validate birthdate using existing function
        print("  Testing existing birthdate validation...")
        try:
            birthdate = parse_and_normalize("01.01.1990")
            print(f"    ✅ Existing birthdate validation: {birthdate}")
        except Exception as e:
            print(f"    ❌ Existing birthdate validation failed: {e}")
            return False
        
        # Test 4: Validate birthdate using DataValidator
        print("  Testing DataValidator birthdate validation...")
        update_birth = MockUpdate("01.01.1990")
        context_birth = MockContext()
        update_birth.effective_message.reply_text = AsyncMock()
        
        success, validated_birthdate = await DataValidator.validate_birthdate(update_birth, context_birth)
        
        if success and validated_birthdate == "01.01.1990":
            print(f"    ✅ DataValidator birthdate validation: {validated_birthdate}")
        else:
            print(f"    ❌ DataValidator birthdate validation failed: success={success}, birthdate={validated_birthdate}")
            return False
        
        # Test 5: Error handling comparison
        print("  Testing error handling...")
        
        # Existing error handling
        try:
            normalize_name("123Invalid")
            print("    ❌ Existing validation should have failed")
            return False
        except Exception as e:
            existing_error = str(e)
            print(f"    ✅ Existing error handling: {existing_error[:30]}...")
        
        # DataValidator error handling
        update_error = MockUpdate()
        context_error = MockContext({"name": "123Invalid"})
        update_error.effective_message.reply_text = AsyncMock()
        
        success, name = await DataValidator.validate_name(update_error, context_error)
        
        if not success:
            print("    ✅ DataValidator error handling works")
            # Check that error message was sent
            update_error.effective_message.reply_text.assert_called_once()
            call_args = update_error.effective_message.reply_text.call_args[0][0]
            if M.ERRORS.NAME_PREFIX in call_args:
                print("    ✅ Error message contains correct prefix")
            else:
                print("    ❌ Error message missing correct prefix")
                return False
        else:
            print("    ❌ DataValidator should have failed validation")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error in validation replacement test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function."""
    print("🚀 Testing DataValidator integration with profile_flow")
    print("=" * 50)
    
    success = True
    
    try:
        success &= await test_profile_flow_validation_replacement()
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 All validation integration tests passed!")
            print("✅ DataValidator can replace existing validation in profile_flow")
        else:
            print("💥 Some validation integration tests failed!")
            print("❌ Need to fix compatibility issues")
            
    except Exception as e:
        print(f"💥 Critical error: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)