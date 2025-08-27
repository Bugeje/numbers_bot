# handlers/extended.py
import tempfile

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from intelligence import get_extended_analysis
from calc.extended import calculate_extended_profile
from output import generate_extended_pdf
from interface import build_after_analysis_keyboard
from helpers import PRESETS, M, MessageManager, Progress, action_typing, action_upload, run_blocking


async def show_extended_only_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Очищаем предыдущие навигационные сообщения
    msg_manager = MessageManager(context)
    await msg_manager.cleanup_tracked_messages()
    
    name = context.user_data.get("name")
    birthdate = context.user_data.get("birthdate")
    core_profile = context.user_data.get("core_profile")

    # расчёт расширенных чисел (как было)
    try:
        extended = calculate_extended_profile(name, birthdate)
        context.user_data["extended_profile"] = extended
    except Exception as e:
        await update.message.reply_text(f"{M.ERRORS.CALC_EXTENDED}\nПодробности: {e}")
        return ConversationHandler.END

    # --- прогресс: ИИ-анализ ---
    await action_typing(update.effective_chat)
    progress = await Progress.start(update, PRESETS["ai"][0])
    await progress.animate(PRESETS["ai"], delay=0.6)

    try:
        analysis_ext = await get_extended_analysis(extended)
        if analysis_ext.startswith("❌"):
            analysis_ext = M.ERRORS.AI_GENERIC
    except Exception:
        analysis_ext = M.ERRORS.AI_GENERIC

    # --- прогресс: PDF ---
    await progress.set(M.PROGRESS.PDF_ONE)
    await action_upload(update.effective_chat)

    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            output_path = tmp.name

        await run_blocking(
            generate_extended_pdf,
            name=name,
            birthdate=birthdate,
            extended=extended,
            analysis_ext=analysis_ext,
            output_path=output_path,
        )

        await progress.set(M.PROGRESS.SENDING_ONE)
        await action_upload(update.effective_chat)

        with open(output_path, "rb") as pdf_file:
            await update.message.reply_document(
                document=pdf_file,
                filename="extended_profile_report.pdf",
                caption=M.CAPTION.EXTENDED,
            )

        await progress.finish()  # ✅ Отчёт готов! (+ автоудаление индикатора)
    except Exception:
        await progress.fail(M.ERRORS.PDF_FAIL)

    # --- финальное сообщение в едином стиле ---
    await msg_manager.send_and_track(
        update, M.HINTS.NEXT_STEP, reply_markup=build_after_analysis_keyboard()
    )
    
    return ConversationHandler.END
