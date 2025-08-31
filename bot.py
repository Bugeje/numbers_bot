#!/usr/bin/env python3
"""
Простой запуск бота без сложной валидации
Используйте этот файл для быстрого запуска
"""

import logging
import re
import asyncio
import signal
import sys

import httpx

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
        print(M.ERRORS.PREFIX + "Не найден TELEGRAM_TOKEN")
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
        
        # Создаем HTTP клиент с настройками для высокой нагрузки
        request = HTTPXRequest(
            read_timeout=settings.http_timeout,
            write_timeout=settings.http_timeout,
            connect_timeout=settings.http_timeout,
            pool_timeout=settings.http_timeout,
        )
        
        # Создаем приложение с настройками для высокой нагрузки
        app = ApplicationBuilder().token(settings.telegram.token).request(request).concurrent_updates(True).build()
        
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
        
        # Добавляем conversation handler первым, чтобы он имел приоритет
        app.add_handler(conv_handler, group=0)
        app.add_handler(days_conversation_handler, group=1)
        app.add_handler(months_conversation_handler, group=1)
        
        # Глобальные обработчики - делаем их более специфичными чтобы они не мешали conversation states
        # Они будут срабатывать только когда нет активной conversation
        app.add_handler(MessageHandler(
            filters.Regex(f"^{re.escape(BTN.CORE)}$") & filters.ChatType.PRIVATE,
            core_profile_ai_and_pdf
        ), group=2)
        app.add_handler(MessageHandler(
            filters.Regex(f"^{re.escape(BTN.PARTNER)}$") & filters.ChatType.PRIVATE,
            request_partner_name
        ), group=2)
        app.add_handler(MessageHandler(
            filters.Regex(f"^{re.escape(BTN.EXTENDED)}$") & filters.ChatType.PRIVATE,
            show_extended_only_profile
        ), group=2)
        app.add_handler(MessageHandler(
            filters.Regex(f"^{re.escape(BTN.BRIDGES)}$") & filters.ChatType.PRIVATE,
            send_bridges_pdf
        ), group=2)
        app.add_handler(MessageHandler(
            filters.Regex(f"^{re.escape(BTN.CYCLES)}$") & filters.ChatType.PRIVATE,
            show_cycles_profile
        ), group=2)
        app.add_handler(MessageHandler(
            filters.Regex(f"^{re.escape(BTN.RESTART)}$") & filters.ChatType.PRIVATE,
            start
        ), group=2)
        
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
                logger.info("Начало очистки ресурсов...")
                
                # Очистка PDF очереди первой, чтобы остановить воркеры
                try:
                    from helpers.pdf_queue import cleanup_pdf_queue
                    await cleanup_pdf_queue()
                    logger.info("PDF очередь очищена")
                except Exception as e:
                    logger.error(f"Ошибка при очистке PDF очереди: {e}")
                
                # Очистка фоновых задач
                try:
                    from helpers.background_tasks import cleanup_background_task_manager
                    await cleanup_background_task_manager()
                    logger.info("Фоновые задачи очищены")
                except Exception as e:
                    logger.error(f"Ошибка при очистке фоновых задач: {e}")
                
                # Очистка HTTP клиентов
                try:
                    from intelligence.engine import cleanup_client
                    await cleanup_client()
                    logger.info("HTTP клиенты очищены")
                except Exception as e:
                    logger.error(f"Ошибка при очистке HTTP клиентов: {e}")
                
                logger.info("Все ресурсы очищены")
            except Exception as e:
                logger.error(f"Ошибка при очистке ресурсов: {e}")
        
        def signal_handler(sig, frame):
            logger.info("Получен сигнал завершения")
            import asyncio
            try:
                # Пытаемся получить текущий event loop
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # Если event loop запущен, планируем задачу на следующий тик
                        future = asyncio.run_coroutine_threadsafe(cleanup_resources(), loop)
                        # Ждем завершения с таймаутом
                        try:
                            future.result(timeout=5.0)
                        except:
                            pass
                    else:
                        # Если event loop не запущен, запускаем его
                        loop.run_until_complete(cleanup_resources())
                except RuntimeError:
                    # Если event loop еще не создан, создаем новый
                    asyncio.run(cleanup_resources())
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
            try:
                logger.info("Начало финальной очистки ресурсов...")
                import asyncio
                # Проверяем, запущен ли event loop
                try:
                    # Пытаемся получить текущий event loop
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # Если event loop запущен, планируем задачу на следующий тик
                        future = asyncio.run_coroutine_threadsafe(cleanup_resources(), loop)
                        # Ждем завершения с таймаутом
                        try:
                            future.result(timeout=5.0)
                        except:
                            pass
                    else:
                        # Если event loop не запущен, запускаем его
                        loop.run_until_complete(cleanup_resources())
                except RuntimeError:
                    # Если event loop еще не создан, создаем новый
                    asyncio.run(cleanup_resources())
                except Exception as e:
                    # Handle any other exceptions during cleanup
                    logger.error(f"Ошибка при финальной очистке: {e}")
                logger.info("Финальная очистка ресурсов завершена")
            except Exception as e:
                logger.error(f"Ошибка при финальной очистке: {e}")
        
    except Exception as e:
        print(f"{M.ERRORS.PREFIX}Ошибка запуска: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()