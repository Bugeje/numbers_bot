#!/usr/bin/env python3
"""
Простой запуск бота без сложной валидации
Используйте этот файл для быстрого запуска
"""

import logging
import re

from config import settings

def main():
    """Запуск бота с простыми настройками."""
    
    if not settings.telegram.token:
        print("❌ Ошибка: Не найден TELEGRAM_TOKEN")
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
        
        from handlers import (
            State,
            core_profile_ai_and_pdf,
            days_conversation_handler,
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
        from utils import BTN
        
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
                    MessageHandler(filters.Regex(f"^{re.escape(BTN.MONTHS)}$"), send_months_pdf),
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
        
        # Глобальные обработчики
        app.add_handler(MessageHandler(filters.Regex(f"^{re.escape(BTN.PARTNER)}$"), request_partner_name))
        app.add_handler(MessageHandler(filters.Regex(f"^{re.escape(BTN.CORE)}$"), core_profile_ai_and_pdf))
        app.add_handler(MessageHandler(filters.Regex(f"^{re.escape(BTN.EXTENDED)}$"), show_extended_only_profile))
        app.add_handler(MessageHandler(filters.Regex(f"^{re.escape(BTN.BRIDGES)}$"), send_bridges_pdf))
        app.add_handler(MessageHandler(filters.Regex(f"^{re.escape(BTN.CYCLES)}$"), show_cycles_profile))
        app.add_handler(MessageHandler(filters.Regex(f"^{re.escape(BTN.MONTHS)}$"), send_months_pdf))
        app.add_handler(MessageHandler(filters.Regex(f"^{re.escape(BTN.RESTART)}$"), start))
        
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        logger.info("✅ Бот запущен успешно!")
        
        # Запускаем бота
        app.run_polling()
        
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()