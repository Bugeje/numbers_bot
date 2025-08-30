#!/usr/bin/env python3
# test_updated_profile_flow.py
"""
Test to verify the updated profile_flow.py with DataValidator integration.
"""

import sys
import os
import asyncio
from unittest.mock import Mock, AsyncMock

# Добавляем корень проекта в PATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock the State class since it's not available in this context
class MockState:
    ASK_NAME = 0
    ASK_BIRTHDATE = 1
    EXTENDED_ANALYSIS = 2
    END = -1

# Add to sys.modules so imports work
import sys
sys.modules['flows.states'] = Mock()
sys.modules['flows.states'].State = MockState

class MockUpdate:
    def __init__(self, message_text=""):
        self.message = Mock() if message_text else None
        if self.message:
            self.message.text = message_text
        self.effective_message = AsyncMock()
        self.effective_chat = Mock()

class MockContext:
    def __init__(self, user_data=None):
        self.user_data = user_data or {}

async def test_updated_profile_flow():
    """Test the updated profile_flow with DataValidator."""
    print("🔍 Testing updated profile_flow with DataValidator...")
    
    try:
        # Import the updated function
        from flows.profile_flow import show_core_profile
        from helpers.data_validator import DataValidator
        from calc import calculate_core_profile
        
        # Test 1: Valid data with update.message
        print("  Testing with valid data (with update.message)...")
        update = MockUpdate("01.01.1990")
        context = MockContext({
            "name": "Тест Пользователь"
        })
        
        # Mock the reply_text method
        update.effective_message.reply_text = AsyncMock()
        
        # Mock MessageManager to avoid actual Telegram API calls
        import helpers
        original_message_manager = helpers.MessageManager
        helpers.MessageManager = Mock()
        helpers.MessageManager.return_value.send_navigation_message = AsyncMock()
        helpers.MessageManager.return_value.cleanup_tracked_messages = AsyncMock()
        
        # Mock calculate_core_profile to avoid complex calculations
        original_calculate_core_profile = calculate_core_profile
        def mock_calculate_core_profile(name, birthdate):
            return {
                "life_path": "1",
                "birthday": "1",
                "expression": "2",
                "soul": "3",
                "personality": "4"
            }
        
        # Temporarily replace the function
        import calc
        calc.calculate_core_profile = mock_calculate_core_profile
        
        # Test the function
        result = await show_core_profile(update, context)
        
        # Restore original functions
        calc.calculate_core_profile = original_calculate_core_profile
        helpers.MessageManager = original_message_manager
        
        if result == MockState.EXTENDED_ANALYSIS:
            print("    ✅ Valid data processed correctly")
            # Check that user_data was updated
            if "core_profile" in context.user_data:
                print("    ✅ Core profile calculated and stored")
            else:
                print("    ❌ Core profile not stored")
                return False
        else:
            print(f"    ❌ Unexpected result: {result}")
            return False
        
        # Test 2: Valid data with birthdate in context.user_data
        print("  Testing with valid data (birthdate in context.user_data)...")
        update2 = MockUpdate()  # No message
        context2 = MockContext({
            "name": "Тест Пользователь",
            "birthdate": "01.01.1990"
        })
        
        # Mock MessageManager again
        helpers.MessageManager = Mock()
        helpers.MessageManager.return_value.send_navigation_message = AsyncMock()
        helpers.MessageManager.return_value.cleanup_tracked_messages = AsyncMock()
        
        # Mock calculate_core_profile again
        calc.calculate_core_profile = mock_calculate_core_profile
        
        # Mock reply_text
        update2.effective_message.reply_text = AsyncMock()
        
        result = await show_core_profile(update2, context2)
        
        # Restore functions
        calc.calculate_core_profile = original_calculate_core_profile
        helpers.MessageManager = original_message_manager
        
        if result == MockState.EXTENDED_ANALYSIS:
            print("    ✅ Valid data with birthdate in context processed correctly")
        else:
            print(f"    ❌ Unexpected result: {result}")
            return False
        
        # Test 3: Invalid name
        print("  Testing with invalid name...")
        context_invalid_name = MockContext({
            "name": "123Invalid"
        })
        
        # Mock MessageManager again
        helpers.MessageManager = Mock()
        helpers.MessageManager.return_value.send_navigation_message = AsyncMock()
        helpers.MessageManager.return_value.cleanup_tracked_messages = AsyncMock()
        
        # Mock reply_text to check if error message is sent
        update_invalid_name = MockUpdate("01.01.1990")
        update_invalid_name.effective_message.reply_text = AsyncMock()
        
        result = await show_core_profile(update_invalid_name, context_invalid_name)
        
        # Restore MessageManager
        helpers.MessageManager = original_message_manager
        
        if result == MockState.ASK_NAME:
            print("    ✅ Invalid name correctly rejected")
            # Check that error message was sent
            update_invalid_name.effective_message.reply_text.assert_called_once()
        else:
            print(f"    ❌ Invalid name not handled correctly: {result}")
            return False
        
        # Test 4: Invalid birthdate
        print("  Testing with invalid birthdate...")
        context_invalid_birthdate = MockContext({
            "name": "Тест Пользователь"
        })
        
        # Mock MessageManager
        helpers.MessageManager = Mock()
        helpers.MessageManager.return_value.send_navigation_message = AsyncMock()
        helpers.MessageManager.return_value.cleanup_tracked_messages = AsyncMock()
        
        # Mock reply_text to check if error message is sent
        update_invalid_birthdate = MockUpdate("invalid-date")
        update_invalid_birthdate.effective_message.reply_text = AsyncMock()
        
        result = await show_core_profile(update_invalid_birthdate, context_invalid_birthdate)
        
        # Restore MessageManager
        helpers.MessageManager = original_message_manager
        
        if result == MockState.ASK_BIRTHDATE:
            print("    ✅ Invalid birthdate correctly rejected")
            # Check that error message was sent
            update_invalid_birthdate.effective_message.reply_text.assert_called_once()
        else:
            print(f"    ❌ Invalid birthdate not handled correctly: {result}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error in updated profile_flow test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function."""
    print("🚀 Testing updated profile_flow with DataValidator")
    print("=" * 50)
    
    success = True
    
    try:
        success &= await test_updated_profile_flow()
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 All updated profile_flow tests passed!")
            print("✅ profile_flow.py successfully integrated with DataValidator")
        else:
            print("💥 Some updated profile_flow tests failed!")
            print("❌ Need to fix integration issues")
            
    except Exception as e:
        print(f"💥 Critical error: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)