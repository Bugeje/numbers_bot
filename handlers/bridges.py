# handlers/bridges.py
import tempfile

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from ai import get_bridges_analysis
from numerology.extended import calculate_bridges
from reports import generate_bridges_pdf
from ui import build_after_analysis_keyboard
from utils import run_blocking
from utils.messages import M
from utils.progress import PRESETS, Progress, action_typing, action_upload


async def send_bridges_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    name = user_data.get("name")
    birthdate = user_data.get("birthdate")
    core_profile = user_data.get("core_profile")
    bridges = user_data.get("bridges")

    # ядро обязательно
    if not (name and birthdate and core_profile):
        await update.message.reply_text(
            f"{M.HINTS.CALC_CORE_FIRST}\n\n{M.HINTS.ASK_BIRTHDATE}\n{M.DATE_FORMATS_NOTE}"
        )
        return ConversationHandler.END

    # если мосты ещё не считались — посчитаем сейчас
    if not bridges:
        try:
            bridges = calculate_bridges(core_profile)
            user_data["bridges"] = bridges
        except Exception:
            await update.message.reply_text(f"{M.ERRORS.CALC_PROFILE}\n{M.HINTS.CALC_CORE_FIRST}")
            return ConversationHandler.END

    # --- прогресс: ИИ-анализ ---
    await action_typing(update.effective_chat)
    progress = await Progress.start(update, PRESETS["ai"][0])
    await progress.animate(PRESETS["ai"], delay=0.6)

    try:
        analysis_bridges = await get_bridges_analysis(bridges)
        if isinstance(analysis_bridges, str) and analysis_bridges.startswith("❌"):
            analysis_bridges = M.ERRORS.AI_GENERIC
    except Exception:
        analysis_bridges = M.ERRORS.AI_GENERIC

    # --- прогресс: PDF ---
    await progress.set(M.PROGRESS.PDF_ONE)
    await action_upload(update.effective_chat)

    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            output_path = tmp.name

        await run_blocking(
            generate_bridges_pdf,
            name=name,
            birthdate=birthdate,
            bridges=bridges,
            analysis_bridges=analysis_bridges,
            output_path=output_path,
        )

        await progress.set(M.PROGRESS.SENDING_ONE)
        await action_upload(update.effective_chat)

        with open(output_path, "rb") as pdf_file:
            await update.message.reply_document(
                document=pdf_file, filename="bridges_report.pdf", caption=M.CAPTION.BRIDGES
            )

        await progress.finish()  # ✅ + автоудаление индикатора
    except Exception:
        await progress.fail(M.ERRORS.PDF_FAIL)

    await update.message.reply_text(M.HINTS.NEXT_STEP, reply_markup=build_after_analysis_keyboard())
    return ConversationHandler.END
