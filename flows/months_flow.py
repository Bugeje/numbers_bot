import tempfile

from telegram import Update
from telegram.ext import ContextTypes

from calc.cycles import MONTH_NAMES, generate_personal_month_cycle_table
from output import create_months_report_pdf
from interface import build_after_analysis_keyboard
from helpers import M, MessageManager, Progress, action_typing, action_upload, run_blocking


async def send_months_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Очищаем предыдущие навигационные сообщения
    msg_manager = MessageManager(context)
    await msg_manager.cleanup_tracked_messages()
    
    name = context.user_data.get("name")
    birthdate = context.user_data.get("birthdate")

    if not name or not birthdate:
        await update.message.reply_text("⚠️ Сначала введите имя и дату рождения.")
        return

    # --- прогресс: расчёты ---
    await action_typing(update.effective_chat)
    progress = await Progress.start(update, "📆 Готовлю анализ месяцев...")

    # Получаем полную таблицу месяцев (1–9)
    raw_month_cycles = generate_personal_month_cycle_table()
    month_cycles = {str(k): [str(v[m]) for m in MONTH_NAMES] for k, v in raw_month_cycles.items()}

    # --- прогресс: PDF ---
    await progress.set(M.PROGRESS.PDF_ONE)
    await action_upload(update.effective_chat)

    # Генерация PDF
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            await run_blocking(create_months_report_pdf, name, birthdate, month_cycles, tmp.name)

            await progress.set(M.PROGRESS.SENDING_ONE)
            await action_upload(update.effective_chat)

            await update.message.reply_document(
                document=open(tmp.name, "rb"), 
                filename="Анализ_месяцев.pdf",
                caption=M.CAPTION.MONTHS
            )

        await progress.finish()
    except Exception:
        await progress.fail(M.ERRORS.PDF_FAIL)

    # Отправляем новое навигационное сообщение (трекаем)
    await msg_manager.send_and_track(
        update, M.HINTS.NEXT_STEP, reply_markup=build_after_analysis_keyboard()
    )
