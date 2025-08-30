# handlers/extended.py
import tempfile

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from intelligence import get_extended_analysis
from calc.extended import calculate_extended_profile
from output import generate_extended_pdf
from helpers import PRESETS, M, FILENAMES, MessageManager, Progress, action_typing, action_upload, run_blocking
from helpers.keyboards import build_after_analysis_keyboard
from helpers.error_handler import ErrorHandler


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
        return await ErrorHandler.handle_calculation_error(
            update, context, e, "расчёта расширенных чисел", ConversationHandler.END
        )

    # --- прогресс: ИИ-анализ ---
    await action_typing(update.effective_chat)
    progress = await Progress.start(update, PRESETS["ai"][0])
    await progress.animate(PRESETS["ai"], delay=0.6)

    try:
        analysis_ext = await get_extended_analysis(extended)
        if M.is_ai_error(analysis_ext):
            analysis_ext = M.ERRORS.AI_GENERIC
    except Exception as e:
        analysis_ext = await ErrorHandler.handle_ai_analysis_error(e)

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
                filename=FILENAMES.EXTENDED_PROFILE,
                caption=M.DOCUMENT_READY,
            )

        await progress.finish()  # ✅ Отчёт готов! (+ автоудаление индикатора)
    except Exception as e:
        await ErrorHandler.handle_pdf_generation_error(update, context, e, progress)

    # --- финальное сообщение в едином стиле ---
    # Отправляем новое навигационное сообщение (трекаем для последующей очистки)
    msg_manager = MessageManager(context)
    await msg_manager.send_navigation_message(
        update, M.HINTS.NEXT_STEP, reply_markup=build_after_analysis_keyboard()
    )
    
    return ConversationHandler.END