import tempfile
import os
import re
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters

from calc.cycles import MONTH_NAMES, generate_personal_month_cycle_table, calculate_personal_year
from calc import calculate_core_profile
from intelligence import get_months_year_analysis
from output import create_months_year_report_pdf
from interface import ASK_MONTHS_YEAR_PROMPT, SELECT_MONTHS_YEAR, build_after_analysis_keyboard
from helpers import M, MessageManager, Progress, action_typing, action_upload, run_blocking, FILENAMES, BTN
from helpers.data_validator import DataValidator

from .base import start


async def ask_months_year_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запрос года для анализа месяцев."""
    # Очищаем предыдущие навигационные сообщения
    msg_manager = MessageManager(context)
    await msg_manager.cleanup_tracked_messages()
    
    # очистим хвосты
    for k in ("months_target_year",):
        context.user_data.pop(k, None)

    await msg_manager.send_and_track(update, ASK_MONTHS_YEAR_PROMPT, parse_mode="Markdown")
    return SELECT_MONTHS_YEAR


async def receive_months_year_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ввода года для анализа месяцев."""
    # Use DataValidator for year validation
    success, year = await DataValidator.validate_year_data(update, context)
    if not success:
        # If validation failed, send error and stay in the same state
        return SELECT_MONTHS_YEAR
    
    context.user_data["months_target_year"] = year
    return await send_months_pdf(update, context)



async def send_months_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Очищаем предыдущие навигационные сообщения
    msg_manager = MessageManager(context)
    await msg_manager.cleanup_tracked_messages()
    
    name = context.user_data.get("name")
    birthdate = context.user_data.get("birthdate")
    core_profile = context.user_data.get("core_profile")
    target_year = context.user_data.get("months_target_year")

    # Use DataValidator for basic profile validation
    profile_validation_result = await DataValidator.validate_basic_profile(update, context)
    success, validated_data = profile_validation_result
    if not success:
        return ConversationHandler.END

    if not target_year:
        await M.send_auto_delete_error(update, context, M.HINTS.MISSING_YEAR)
        return ConversationHandler.END

    # Автоматически рассчитываем core_profile, если его нет
    if not core_profile:
        try:
            core_profile = calculate_core_profile(name, birthdate)
            context.user_data["core_profile"] = core_profile
        except Exception as e:
            await M.send_auto_delete_error(update, context, M.format_error_details(M.ERRORS.CALC_PROFILE, str(e)))
            return ConversationHandler.END

    # --- прогресс: расчёты ---
    await action_typing(update.effective_chat)
    progress = await Progress.start(update, M.PROGRESS.PREPARE_MONTHS.format(year=target_year))

    # Используем выбранный пользователем год
    
    # Вычисляем персональный год для выбранного года
    personal_year_str = calculate_personal_year(birthdate, target_year)
    personal_year = int(personal_year_str.split('(')[0])  # Извлекаем базовое число
    
    # Получаем таблицу месяцев для данного персонального года
    raw_month_cycles = generate_personal_month_cycle_table()
    months_data = [str(raw_month_cycles[personal_year][m]) for m in MONTH_NAMES]
    month_cycles = {str(k): [str(v[m]) for m in MONTH_NAMES] for k, v in raw_month_cycles.items()}

    # --- прогресс: AI-анализ ---
    await progress.set(M.PROGRESS.AI_ANALYSIS)
    try:
        # Используем выбранный пользователем год
        ai_analysis = await get_months_year_analysis(
            profile=core_profile,
            birthdate=birthdate,
            personal_year=personal_year,
            year=target_year,
        )
        if M.is_ai_error(ai_analysis):
            ai_analysis = M.ERRORS.AI_GENERIC
    except Exception:
        ai_analysis = M.ERRORS.AI_GENERIC

    # --- прогресс: PDF ---
    await progress.set(M.PROGRESS.PDF_ONE)
    await action_upload(update.effective_chat)

    # Генерация PDF
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp_path = tmp.name
            
        # Всегда используем полный шаблон с AI анализом
        await run_blocking(
            create_months_year_report_pdf, 
            name, 
            birthdate, 
            target_year,
            personal_year,
            months_data, 
            core_profile,
            ai_analysis,
            tmp_path
        )
        
        await progress.set(M.PROGRESS.SENDING_ONE)
        await action_upload(update.effective_chat)

        with open(tmp_path, "rb") as pdf_file:
            await update.message.reply_document(
                document=pdf_file, 
                filename=FILENAMES.MONTHS,
                caption=M.DOCUMENT_READY
            )

        # Cleanup temporary file
        try:
            os.unlink(tmp_path)
        except Exception:
            pass  # Ignore cleanup errors

        await progress.finish()
    except Exception:
        await progress.fail(M.ERRORS.PDF_FAIL)

    # Отправляем новое навигационное сообщение (трекаем для последующей очистки)
    msg_manager = MessageManager(context)
    await msg_manager.send_navigation_message(
        update, M.HINTS.NEXT_STEP, reply_markup=build_after_analysis_keyboard()
    )

    return ConversationHandler.END


months_conversation_handler = ConversationHandler(
    entry_points=[
        MessageHandler(filters.Regex(f"^{re.escape(BTN.MONTHS)}$"), ask_months_year_start),
    ],
    states={
        SELECT_MONTHS_YEAR: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_months_year_text),
        ],
    },
    fallbacks=[MessageHandler(filters.Regex(f"^{re.escape(BTN.RESTART)}$"), start)],
)