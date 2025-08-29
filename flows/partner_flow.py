import tempfile

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from intelligence import get_compatibility_interpretation
from calc import calculate_core_profile
from output import generate_partner_pdf
from interface import build_after_analysis_keyboard
from helpers import M, MessageManager, Progress, action_typing, action_upload, parse_and_normalize, run_blocking, FILENAMES

from .states import State


async def request_partner_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Очищаем предыдущие навигационные сообщения
    msg_manager = MessageManager(context)
    await msg_manager.cleanup_tracked_messages()
    
    context.user_data["selecting_partner"] = True
    await msg_manager.send_and_track(update, M.HINTS.ASK_PARTNER_NAME)
    return State.ASK_PARTNER_NAME


async def save_partner_name_and_ask_birthdate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("selecting_partner"):
        return

    # Очищаем промпт о вводе имени
    msg_manager = MessageManager(context)
    await msg_manager.cleanup_tracked_messages()

    context.user_data["partner_name"] = update.message.text.strip()
    await msg_manager.send_and_track(
        update,
        M.HINTS.ASK_PARTNER_BIRTHDATE
    )

    return State.ASK_PARTNER_BIRTHDATE


async def receive_partner_birthdate_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Очищаем промпт о вводе даты
    msg_manager = MessageManager(context)
    await msg_manager.cleanup_tracked_messages()
    
    try:
        date_str = (update.message.text or "").strip()
        normalized = parse_and_normalize(date_str)
        context.user_data["partner_birthdate"] = normalized
        return await generate_compatibility(update, context)
    except Exception as e:
        await M.send_auto_delete_error(update, context, f"{M.ERRORS.DATE_PREFIX}{e}\n{M.HINTS.RETRY_PARTNER_DATE}")
        return State.ASK_PARTNER_BIRTHDATE


async def generate_compatibility(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        name_a = context.user_data["name"]
        birth_a = context.user_data["birthdate"]
        profile_a = context.user_data["core_profile"]

        name_b = context.user_data["partner_name"]
        birth_b = context.user_data.get("partner_birthdate")

        if not birth_b and update.message:
            birth_b = update.message.text.strip()
            context.user_data["partner_birthdate"] = birth_b
        elif not birth_b:
            await M.send_auto_delete_error(update, context, M.HINTS.MISSING_PARTNER_DATA)
            return ConversationHandler.END

        # --- прогресс: расчёты ---
        await action_typing(update.effective_chat)
        progress = await Progress.start(update, "💞 Готовлю анализ совместимости...")

        profile_b = calculate_core_profile(name_b, birth_b)
        
        # --- прогресс: ИИ-анализ ---
        await progress.set("🤖 Получаю AI-анализ совместимости...")

        try:
            interpretation = await get_compatibility_interpretation(profile_a, profile_b)
            if M.is_ai_error(interpretation):
                interpretation = M.ERRORS.AI_GENERIC
        except Exception:
            interpretation = M.ERRORS.AI_GENERIC

        # --- прогресс: PDF ---
        await progress.set(M.PROGRESS.PDF_ONE)
        await action_upload(update.effective_chat)

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                await run_blocking(
                    generate_partner_pdf,
                    name_a,
                    birth_a,
                    profile_a,
                    name_b,
                    birth_b,
                    profile_b,
                    interpretation=interpretation,
                    output_path=tmp.name,
                )
                
                await progress.set(M.PROGRESS.SENDING_ONE)
                await action_upload(update.effective_chat)
                
                with open(tmp.name, "rb") as pdf_file:
                    await update.effective_message.reply_document(
                        pdf_file, 
                        filename=FILENAMES.PARTNER_COMPATIBILITY,
                        caption=M.DOCUMENT_READY
                    )

            await progress.finish()
        except Exception:
            await progress.fail(M.ERRORS.PDF_FAIL)

        context.user_data.pop("selecting_partner", None)

        # Отправляем навигационное сообщение с трекингом для автоудаления
        msg_manager = MessageManager(context)
        # Отправляем новое навигационное сообщение (НЕ трекаем - это постоянная навигация)
        await update.effective_message.reply_text(
            M.HINTS.NEXT_STEP, reply_markup=build_after_analysis_keyboard()
        )

        return ConversationHandler.END

    except Exception as e:
        await M.send_auto_delete_error(update, context, M.format_error(str(e)))
        return ConversationHandler.END
