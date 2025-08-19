# handlers/core_profile.py
import tempfile
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from numerology import calculate_core_profile
from reports import generate_core_pdf
from ai import get_ai_analysis
from ui import build_after_analysis_keyboard
from .states import State
from utils import (
    run_blocking,
    parse_and_normalize,
    normalize_name,
    Progress, 
    PRESETS, 
    action_typing, action_upload,
    M
)


async def show_core_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Считает и показывает числа ядра личности. ИИ не вызывается."""
    # --- validate name ---
    try:
        name = normalize_name(context.user_data.get("name"))
    except Exception as e:
        await update.effective_message.reply_text(
            f"{M.ERRORS.NAME_PREFIX}{e}\n\n{M.HINTS.REENTER_NAME}"
        )
        return State.ASK_NAME

    # --- validate birthdate ---
    raw_birthdate = update.message.text.strip() if update.message else context.user_data.get("birthdate")
    try:
        birthdate = parse_and_normalize(raw_birthdate)
        # защита от будущей даты (если удалось распарсить в ДД.ММ.ГГГГ)
        try:
            dt = datetime.strptime(birthdate, "%d.%m.%Y")
            if dt.date() > datetime.now().date():
                raise ValueError(M.ERRORS.DATE_FUTURE)
        except ValueError:
            # если формат иной — полагаемся на parse_and_normalize
            pass
    except Exception as e:
        await update.effective_message.reply_text(
            f"{M.ERRORS.DATE_PREFIX}{e}\n\n{M.DATE_FORMATS_NOTE}\n{M.HINTS.REENTER_DATE}"
        )
        return State.ASK_BIRTHDATE

    # сохранить нормализованную дату
    context.user_data["birthdate"] = birthdate

    # --- calculate core profile (без ИИ) ---
    try:
        profile = calculate_core_profile(name, birthdate)
        context.user_data["core_profile"] = profile
    except Exception as e:
        await update.effective_message.reply_text(f"{M.ERRORS.CALC_PROFILE}\nПодробности: {e}")
        return ConversationHandler.END

    # --- показать краткий итог и клавиатуру следующего шага ---
    await update.effective_message.reply_text(
        M.format_core_summary(name, birthdate, profile),
        parse_mode="Markdown"
    )
    await update.effective_message.reply_text(
        M.HINTS.NEXT_STEP,
        reply_markup=build_after_analysis_keyboard()
    )

    # остаёмся в режиме ожидания кнопок (в т.ч. «Ядро личности» для ИИ+PDF)
    return State.EXTENDED_ANALYSIS
    

async def core_profile_ai_and_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ИИ-анализ и PDF — ТОЛЬКО по нажатию кнопки 'Ядро личности'."""
    name = context.user_data.get("name")
    birthdate = context.user_data.get("birthdate")
    profile = context.user_data.get("core_profile")

    if not (name and birthdate and profile):
        await update.effective_message.reply_text("Сначала рассчитаем ядро личности. Введите дату рождения.")
        return State.ASK_BIRTHDATE

    await action_typing(update.effective_chat)
    progress = await Progress.start(update, PRESETS["ai"][0])
    await progress.animate(PRESETS["ai"], delay=0.6)

    try:
        analysis = await get_ai_analysis(profile)
        if analysis.startswith("❌") or analysis.startswith("[Сетевая ошибка"):
            analysis = M.ERRORS.AI_GENERIC
    except Exception:
        analysis = M.ERRORS.AI_GENERIC

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
            output_path=output_path
        )

        await progress.set(M.PROGRESS.SENDING_ONE)
        await action_upload(update.effective_chat)

        with open(output_path, "rb") as pdf_file:
            await update.effective_message.reply_document(
                document=pdf_file,
                filename="core_profile_report.pdf",
                caption="📄 Ваш отчёт о ядре личности"
            )

        await progress.finish()
    except Exception as e:
        await progress.fail(M.ERRORS.PDF_FAIL)
        await update.effective_message.reply_text(f"Не удалось сформировать PDF: {e}")

    await update.effective_message.reply_text(
        M.HINTS.NEXT_STEP,
        reply_markup=build_after_analysis_keyboard()
    )
    return State.EXTENDED_ANALYSIS
