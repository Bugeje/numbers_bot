# flows/profile_flow.py
import tempfile
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from intelligence import get_ai_analysis
from calc import calculate_core_profile
from output import generate_core_pdf
from helpers import (
    PRESETS,
    M,
    FILENAMES,
    MessageManager,
    Progress,
    action_typing,
    action_upload,
    run_blocking,
)
from helpers.data_validator import DataValidator
from helpers.keyboards import build_after_analysis_keyboard
from helpers.error_handler import ErrorHandler, FlowErrorHandler

from .states import State


async def show_core_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Считает и показывает числа ядра личности. ИИ не вызывается."""
    # --- validate name using DataValidator ---
    name_validation_result = await DataValidator.validate_name(update, context)
    success, name = name_validation_result
    if not success:
        return State.ASK_NAME

    # --- validate birthdate using DataValidator ---
    birthdate_validation_result = await DataValidator.validate_birthdate(update, context)
    success, birthdate = birthdate_validation_result
    if not success:
        return State.ASK_BIRTHDATE

    # сохранить нормализованную дату
    context.user_data["birthdate"] = birthdate

    # --- calculate core profile (без ИИ) ---
    try:
        profile = calculate_core_profile(name, birthdate)
        context.user_data["core_profile"] = profile
    except Exception as e:
        return await ErrorHandler.handle_calculation_error(
            update, context, e, "расчёта ядра личности", ConversationHandler.END
        )

    # --- показать краткий итог и клавиатуру следующего шага ---
    msg_manager = MessageManager(context)
    
    # Отправляем краткий итог (не трекаем - это важная информация)
    await update.effective_message.reply_text(
        M.format_core_summary(name, birthdate, profile), parse_mode="Markdown"
    )
    
    # Отправляем навигационное сообщение (трекаем для последующей очистки)
    await msg_manager.send_navigation_message(
        update, M.HINTS.NEXT_STEP, reply_markup=build_after_analysis_keyboard()
    )

    # остаёмся в режиме ожидания кнопок (в т.ч. «Ядро личности» для ИИ+PDF)
    return State.EXTENDED_ANALYSIS


async def core_profile_ai_and_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ИИ-анализ и PDF — ТОЛЬКО по нажатию кнопки 'Ядро личности'."""
    # Очищаем предыдущие навигационные сообщения
    msg_manager = MessageManager(context)
    await msg_manager.cleanup_tracked_messages()
    
    name = context.user_data.get("name")
    birthdate = context.user_data.get("birthdate")
    profile = context.user_data.get("core_profile")

    if not (name and birthdate and profile):
        await update.effective_message.reply_text(
            f"{M.HINTS.CALC_CORE_FIRST}\n\n{M.HINTS.ASK_BIRTHDATE}"
        )
        return State.ASK_BIRTHDATE

    await action_typing(update.effective_chat)
    progress = await Progress.start(update, PRESETS["ai"][0])
    await progress.animate(PRESETS["ai"], delay=0.6)

    try:
        analysis = await get_ai_analysis(profile)
        if M.is_ai_error(analysis):
            analysis = M.ERRORS.AI_GENERIC
    except Exception as e:
        analysis = await ErrorHandler.handle_ai_analysis_error(e)

    await progress.set(M.PROGRESS.PDF_ONE)
    await action_upload(update.effective_chat)

    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            output_path = tmp.name

        await run_blocking(
            generate_core_pdf,
            name=name,
            birthdate=birthdate,
            profile=profile,
            analysis=analysis,
            output_path=output_path,
        )

        await progress.set(M.PROGRESS.SENDING_ONE)
        await action_upload(update.effective_chat)

        with open(output_path, "rb") as pdf_file:
            await update.effective_message.reply_document(
                document=pdf_file, filename=FILENAMES.CORE_PROFILE, caption=M.DOCUMENT_READY
            )

        await progress.finish()
    except Exception as e:
        await ErrorHandler.handle_pdf_generation_error(update, context, e, progress)

    # Отправляем новое навигационное сообщение (трекаем для последующей очистки)
    msg_manager = MessageManager(context)
    await msg_manager.send_navigation_message(
        update, M.HINTS.NEXT_STEP, reply_markup=build_after_analysis_keyboard()
    )
    return State.EXTENDED_ANALYSIS