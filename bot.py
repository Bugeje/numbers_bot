#!/usr/bin/env python3
"""
Refactored bot implementation with improved predictability and maintainability.
"""

import logging
import re
import asyncio
import signal
import sys
from typing import Optional

from config import settings
from helpers import M  # Message helpers

# Import telegram components at module level to avoid NameError
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
from telegram.request import HTTPXRequest

# Global application instance
_app_instance = None


class BotRunner:
    """Encapsulates bot initialization, running, and cleanup logic."""
    
    def __init__(self):
        self.app = None
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self):
        """Initialize the bot application with all handlers."""
        self.logger.info("Initializing bot application...")
        
        try:
            from flows import (
                State,
                core_profile_ai_and_pdf,
                days_conversation_handler,
                months_conversation_handler,
                receive_birthdate_text,
                receive_partner_birthdate_text,
                request_partner_name,
                save_name_and_ask_birthdate,
                save_partner_name_and_ask_birthdate,
                send_bridges_pdf,
                send_months_pdf,
                show_cycles_profile,
                show_extended_only_profile,
                start,
            )
            from helpers import BTN
            
            # Configure logging with appropriate level
            logging.basicConfig(
                level=logging.DEBUG if settings.debug else logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
            # Create HTTP client with optimized settings for high load
            request = HTTPXRequest(
                read_timeout=settings.http_timeout,
                write_timeout=settings.http_timeout,
                connect_timeout=settings.http_timeout,
                pool_timeout=settings.http_timeout,
            )
            
            # Create application with optimized settings
            self.app = ApplicationBuilder().token(settings.telegram.token).request(request).concurrent_updates(True).build()
            
            # Setup conversation handlers
            self._setup_conversation_handlers()
            
            # Setup global handlers
            self._setup_global_handlers()
            
            # Setup error handler
            self.app.add_error_handler(self._error_handler)
            
            self.logger.info("✅ Bot application initialized successfully!")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize bot: {e}")
            raise
    
    def _setup_conversation_handlers(self):
        """Setup the main conversation handler for user onboarding."""
        from flows import (
            State,
            core_profile_ai_and_pdf,
            receive_birthdate_text,
            save_name_and_ask_birthdate,
            request_partner_name,
            save_partner_name_and_ask_birthdate,
            receive_partner_birthdate_text,
            show_extended_only_profile,
            send_bridges_pdf,
            show_cycles_profile,
            start,
        )
        from helpers import BTN
        
        conv_handler = ConversationHandler(
            entry_points=[
                CommandHandler("start", start),
                MessageHandler(filters.Regex(f"^{re.escape(BTN.RESTART)}$"), start),
            ],
            states={
                State.ASK_NAME: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, save_name_and_ask_birthdate)
                ],
                State.ASK_BIRTHDATE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, receive_birthdate_text)
                ],
                State.EXTENDED_ANALYSIS: [
                    MessageHandler(filters.Regex(f"^{re.escape(BTN.PARTNER)}$"), request_partner_name),
                    MessageHandler(filters.Regex(f"^{re.escape(BTN.CORE)}$"), core_profile_ai_and_pdf),
                    MessageHandler(
                        filters.Regex(f"^{re.escape(BTN.EXTENDED)}$"), show_extended_only_profile
                    ),
                    MessageHandler(filters.Regex(f"^{re.escape(BTN.BRIDGES)}$"), send_bridges_pdf),
                    MessageHandler(filters.Regex(f"^{re.escape(BTN.CYCLES)}$"), show_cycles_profile),
                ],
                State.ASK_PARTNER_NAME: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, save_partner_name_and_ask_birthdate)
                ],
                State.ASK_PARTNER_BIRTHDATE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, receive_partner_birthdate_text)
                ],
            },
            fallbacks=[MessageHandler(filters.Regex(f"^{re.escape(BTN.RESTART)}$"), start)],
        )
        
        # Add conversation handler with highest priority
        self.app.add_handler(conv_handler, group=0)
    
    def _setup_global_handlers(self):
        """Setup global handlers for features available after onboarding."""
        from telegram.ext import MessageHandler, filters
        from flows import (
            days_conversation_handler,
            months_conversation_handler,
            request_partner_name,
            show_extended_only_profile,
            send_bridges_pdf,
            show_cycles_profile,
            start,
        )
        from helpers import BTN
        
        # Add specialized conversation handlers
        self.app.add_handler(days_conversation_handler, group=1)
        self.app.add_handler(months_conversation_handler, group=1)
        
        # Global handlers - only work when user has completed onboarding
        # These have lower priority than conversation handlers
        self.app.add_handler(MessageHandler(
            filters.Regex(f"^{re.escape(BTN.PARTNER)}$") & filters.ChatType.PRIVATE,
            self._create_global_handler(request_partner_name)
        ), group=2)
        
        self.app.add_handler(MessageHandler(
            filters.Regex(f"^{re.escape(BTN.EXTENDED)}$") & filters.ChatType.PRIVATE,
            self._create_global_handler(show_extended_only_profile)
        ), group=2)
        
        self.app.add_handler(MessageHandler(
            filters.Regex(f"^{re.escape(BTN.BRIDGES)}$") & filters.ChatType.PRIVATE,
            self._create_global_handler(send_bridges_pdf)
        ), group=2)
        
        self.app.add_handler(MessageHandler(
            filters.Regex(f"^{re.escape(BTN.CYCLES)}$") & filters.ChatType.PRIVATE,
            self._create_global_handler(show_cycles_profile)
        ), group=2)
        
        self.app.add_handler(MessageHandler(
            filters.Regex(f"^{re.escape(BTN.RESTART)}$") & filters.ChatType.PRIVATE,
            start
        ), group=2)
    
    def _create_global_handler(self, handler_func):
        """Create a wrapper for global handlers that checks user onboarding status."""
        async def wrapper(update, context):
            # Check if user has completed onboarding
            if not self._is_user_onboarded(context):
                # Don't handle this globally, let conversation flow handle it
                return None
            return await handler_func(update, context)
        return wrapper
    
    def _is_user_onboarded(self, context) -> bool:
        """Check if user has completed the onboarding process."""
        return (
            context.user_data.get("name") and 
            context.user_data.get("birthdate") and 
            context.user_data.get("core_profile")
        )
    
    async def _error_handler(self, update, context):
        """Centralized error handler for the bot."""
        # Log the error
        self.logger.error(f"Bot error: {context.error}", exc_info=True)
        
        # Send user-friendly error message (if there's an update)
        if update and update.effective_message:
            try:
                await M.send_auto_delete_error(
                    update, context, 
                    M.ERRORS.GENERIC_ERROR,
                    delete_after=7.0
                )
            except Exception:
                # If we can't send a message, just log it
                self.logger.error("Failed to send error message to user", exc_info=True)
    
    def run(self):
        """Run the bot application."""
        if not self.app:
            raise RuntimeError("Bot not initialized. Call initialize() first.")
        
        self.logger.info("🚀 Starting bot...")
        # Use run_polling directly - it manages its own event loop
        self.app.run_polling(drop_pending_updates=True)
    
    async def cleanup(self):
        """Clean up resources when shutting down."""
        self.logger.info("Starting cleanup process...")
        
        try:
            # Clean up PDF queue first to stop workers
            try:
                from helpers.pdf_queue import cleanup_pdf_queue
                await cleanup_pdf_queue()
                self.logger.info("PDF queue cleaned up")
            except Exception as e:
                self.logger.error(f"Error cleaning up PDF queue: {e}")
            
            # Clean up background tasks
            try:
                from helpers.background_tasks import cleanup_background_task_manager
                await cleanup_background_task_manager()
                self.logger.info("Background tasks cleaned up")
            except Exception as e:
                self.logger.error(f"Error cleaning up background tasks: {e}")
            
            # Clean up HTTP clients
            try:
                from intelligence.engine import cleanup_client
                await cleanup_client()
                self.logger.info("HTTP clients cleaned up")
            except Exception as e:
                self.logger.error(f"Error cleaning up HTTP clients: {e}")
            
            self.logger.info("Cleanup process completed")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


def _signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger = logging.getLogger(__name__)
    logger.info(f"Received signal {signum}, shutting down...")
    
    # Get the global bot runner instance
    global _app_instance
    if _app_instance:
        # Run cleanup in a new event loop since we're outside of async context
        try:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(_app_instance.cleanup())
            loop.close()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    # Exit the application
    sys.exit(0)


def _setup_signal_handlers():
    """Setup signal handlers for graceful shutdown."""
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)


def main():
    """Main entry point for the bot."""
    # Check for required token
    if not settings.telegram.token:
        print(M.ERRORS.PREFIX + "TELEGRAM_TOKEN not found")
        print("Create a .env file and add:")
        print("TELEGRAM_TOKEN=your_token_here")
        return
    
    print(f"🚀 Starting bot with token: {settings.telegram.token[:10]}...")
    
    try:
        # Create and initialize bot runner
        global _app_instance
        _app_instance = BotRunner()
        
        # Setup signal handlers for graceful shutdown
        _setup_signal_handlers()
        
        # Initialize the bot
        # Create a new event loop for initialization
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_app_instance.initialize())
        # Don't close the loop here, let run_polling use it
        
        # Run the bot (this will block until the bot is stopped)
        _app_instance.run()
        
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"{M.ERRORS.PREFIX}Bot startup error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Ensure cleanup happens even if there's an error
        if _app_instance:
            try:
                # Run cleanup in a new event loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(_app_instance.cleanup())
                loop.close()
            except Exception as e:
                print(f"{M.ERRORS.PREFIX}Cleanup error: {e}")


if __name__ == "__main__":
    main()