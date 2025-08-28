import tempfile
import os
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

from calc.cycles import MONTH_NAMES, generate_personal_month_cycle_table, calculate_personal_year
from calc import calculate_core_profile
from intelligence import get_months_year_analysis
from output import create_months_year_report_pdf
from interface import build_after_analysis_keyboard
from helpers import M, MessageManager, Progress, action_typing, action_upload, run_blocking


async def send_months_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Очищаем предыдущие навигационные сообщения
    msg_manager = MessageManager(context)
    await msg_manager.cleanup_tracked_messages()
    
    name = context.user_data.get("name")
    birthdate = context.user_data.get("birthdate")
    core_profile = context.user_data.get("core_profile")

    if not name or not birthdate:
        await update.message.reply_text("⚠️ Сначала введите имя и дату рождения.")
        return

    # Автоматически рассчитываем core_profile, если его нет
    if not core_profile:
        try:
            core_profile = calculate_core_profile(name, birthdate)
            context.user_data["core_profile"] = core_profile
        except Exception:
            # Если не удалось рассчитать, продолжаем без AI
            core_profile = None

    # --- прогресс: расчёты ---
    await action_typing(update.effective_chat)
    progress = await Progress.start(update, "📆 Готовлю анализ месяцев...")

    # Используем текущий год как целевой год для анализа
    target_year = datetime.today().year
    
    # Вычисляем персональный год для целевого года
    personal_year_str = calculate_personal_year(birthdate, target_year)
    personal_year = int(personal_year_str.split('(')[0])  # Извлекаем базовое число
    
    # Получаем таблицу месяцев для данного персонального года
    raw_month_cycles = generate_personal_month_cycle_table()
    months_data = [str(raw_month_cycles[personal_year][m]) for m in MONTH_NAMES]
    month_cycles = {str(k): [str(v[m]) for m in MONTH_NAMES] for k, v in raw_month_cycles.items()}

    # --- прогресс: AI-анализ (если есть профиль) ---
    ai_analysis = None
    if core_profile:
        await progress.set("🤖 Генерирую AI-анализ месяца/года...")
        try:
            # Используем тот же целевой год, что и для расчёта персонального года
            ai_analysis = await get_months_year_analysis(
                profile=core_profile,
                birthdate=birthdate,
                personal_year=personal_year,
                year=target_year,
            )
            if isinstance(ai_analysis, str) and ai_analysis.startswith("❌"):
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
            
            if ai_analysis and ai_analysis != M.ERRORS.AI_GENERIC:
                # Используем шаблон с AI анализом
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
                filename = "Анализ_месяцев_с_ИИ.pdf"
                caption = M.CAPTION.MONTHS_YEAR
            else:
                # Используем тот же шаблон, но без AI анализа или с ошибкой
                await run_blocking(
                    create_months_year_report_pdf, 
                    name, 
                    birthdate, 
                    target_year,
                    personal_year,
                    months_data, 
                    core_profile,
                    ai_analysis or "Ошибка: AI анализ недоступен",
                    tmp_path
                )
                filename = "Анализ_месяцев.pdf"
                caption = M.CAPTION.MONTHS

            await progress.set(M.PROGRESS.SENDING_ONE)
            await action_upload(update.effective_chat)

            with open(tmp_path, "rb") as pdf_file:
                await update.message.reply_document(
                    document=pdf_file, 
                    filename=filename,
                    caption=caption
                )

        # Cleanup temporary file
        try:
            os.unlink(tmp_path)
        except Exception:
            pass  # Ignore cleanup errors

        await progress.finish()
    except Exception:
        await progress.fail(M.ERRORS.PDF_FAIL)

    # Отправляем новое навигационное сообщение (трекаем)
    await msg_manager.send_and_track(
        update, M.HINTS.NEXT_STEP, reply_markup=build_after_analysis_keyboard()
    )

