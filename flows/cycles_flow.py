from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from calc.cycles import (
    calculate_pinnacles_with_periods,
    generate_personal_year_table,
    split_years_by_pinnacles,
)
from output import generate_cycles_pdf
from interface import build_after_analysis_keyboard
from helpers import PRESETS, M, MessageManager, Progress, action_typing, action_upload, run_blocking


async def show_cycles_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Очищаем предыдущие навигационные сообщения
        msg_manager = MessageManager(context)
        await msg_manager.cleanup_tracked_messages()
        
        name = context.user_data["name"]
        birthdate = context.user_data["birthdate"]
        life_path = context.user_data["core_profile"]["life_path"]

        # --- прогресс: расчёты ---
        await action_typing(update.effective_chat)
        progress = await Progress.start(update, "🔄 Готовлю анализ по циклам и годам...")

        # Вычисления
        personal_years = generate_personal_year_table(birthdate)
        pinnacles = calculate_pinnacles_with_periods(birthdate, life_path)
        personal_year_blocks = split_years_by_pinnacles(birthdate)

        # --- прогресс: PDF ---
        await progress.set(M.PROGRESS.PDF_ONE)
        await action_upload(update.effective_chat)

        # Генерация PDF
        try:
            pdf_path = await run_blocking(
                generate_cycles_pdf, name, birthdate, personal_years, pinnacles, personal_year_blocks
            )

            await progress.set(M.PROGRESS.SENDING_ONE)
            await action_upload(update.effective_chat)

            with open(pdf_path, "rb") as f:
                await update.message.reply_document(
                    document=f, filename="Вершины_года.pdf", caption=M.CAPTION.CYCLES
                )

            await progress.finish()
        except Exception:
            await progress.fail(M.ERRORS.PDF_FAIL)

        # Отправляем новое навигационное сообщение (трекаем)
        await msg_manager.send_and_track(
            update, M.HINTS.NEXT_STEP, reply_markup=build_after_analysis_keyboard()
        )

        return ConversationHandler.END

    except Exception as e:
        await update.message.reply_text("❌ Произошла ошибка при формировании анализа циклов.")
        raise e
