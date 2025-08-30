#!/usr/bin/env python3
"""
Простой запуск бота без сложной валидации
Используйте этот файл для быстрого запуска
"""

import logging
import re

from config import settings
from helpers import M  # Переносим сюда


async def error_handler(update, context):
    """Обработчик ошибок для бота."""
    import traceback
    
    # Логируем ошибку
    logger = logging.getLogger(__name__)
    logger.error(f"Ошибка в боте: {context.error}")
    logger.error(traceback.format_exc())
    
    # Отправляем пользователю об ошибке (если есть update)
    if update and update.effective_message:
        try:
            await M.send_auto_delete_error(
                update, context, 
                M.ERRORS.GENERIC_ERROR,
                delete_after=7.0
            )
        except Exception:
            # Если и это не сработало, просто логируем
            logger.error("Не удалось отправить сообщение об ошибке")


def main():
    """Запуск бота с простыми настройками."""
    
    if not settings.telegram.token:
        print(M.ERRORS.NO_TOKEN)
        print("Создайте файл .env и добавьте:")
        print("TELEGRAM_TOKEN=ваш_токен_здесь")
        return
    
    print(f"🚀 Запуск бота с токеном: {settings.telegram.token[:10]}...")
    
    try:
        from telegram.ext import (
            ApplicationBuilder,
            CommandHandler,
            ConversationHandler,
            MessageHandler,
            filters,
        )
        from telegram.request import HTTPXRequest
        
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
        
        # Создаем HTTP клиент
        request = HTTPXRequest(
            read_timeout=settings.http_timeout,
            write_timeout=settings.http_timeout,
            connect_timeout=settings.http_timeout,
            pool_timeout=settings.http_timeout,
        )
        
        # Создаем приложение
        app = ApplicationBuilder().token(settings.telegram.token).request(request).build()
        
        # Настраиваем обработчики
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
        
        app.add_handler(conv_handler)
        app.add_handler(days_conversation_handler)
        app.add_handler(months_conversation_handler)
        
        # Глобальные обработчики
        app.add_handler(MessageHandler(filters.Regex(f"^{re.escape(BTN.PARTNER)}$"), request_partner_name))
        app.add_handler(MessageHandler(filters.Regex(f"^{re.escape(BTN.CORE)}$"), core_profile_ai_and_pdf))
        app.add_handler(MessageHandler(filters.Regex(f"^{re.escape(BTN.EXTENDED)}$"), show_extended_only_profile))
        app.add_handler(MessageHandler(filters.Regex(f"^{re.escape(BTN.BRIDGES)}$"), send_bridges_pdf))
        app.add_handler(MessageHandler(filters.Regex(f"^{re.escape(BTN.CYCLES)}$"), show_cycles_profile))
        app.add_handler(MessageHandler(filters.Regex(f"^{re.escape(BTN.RESTART)}$"), start))
        
        # Добавляем обработчик ошибок
        app.add_error_handler(error_handler)
        
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        logger.info("✅ Бот запущен успешно!")
        
        # Добавляем обработчик очистки ресурсов
        import signal
        import sys
        
        async def cleanup_resources():
            """Очистка ресурсов при завершении."""
            try:
                from intelligence.engine import cleanup_client
                await cleanup_client()
                logger.info("Ресурсы очищены")
            except Exception as e:
                logger.error(f"Ошибка при очистке ресурсов: {e}")
        
        def signal_handler(sig, frame):
            logger.info("Получен сигнал завершения")
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(cleanup_resources())
            except Exception as e:
                logger.error(f"Ошибка при завершении: {e}")
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Запускаем бота
        try:
            app.run_polling()
        finally:
            # Очистка при нормальном завершении
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(cleanup_resources())
            except Exception as e:
                logger.error(f"Ошибка при финальной очистке: {e}")
        
    except Exception as e:
        print(f"{M.ERRORS.STARTUP_ERROR}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()