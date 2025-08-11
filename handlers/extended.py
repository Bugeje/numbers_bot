from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
import tempfile

from numerology.extended import calculate_extended_profile
from ai import get_extended_analysis
from reports import generate_extended_pdf
from ui import build_after_analysis_keyboard
from .states import State


async def show_extended_only_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = context.user_data.get("name")
    birthdate = context.user_data.get("birthdate")
    core_profile = context.user_data.get("core_profile")

    if not all([name, birthdate, core_profile]):
        await update.message.reply_text("❌ Недостаточно данных для анализа.")
        return State.State.EXTENDED_ANALYSIS

    await update.message.reply_text("🔄 Считаю расширенные числа...")

    extended = calculate_extended_profile(name, birthdate)
    ai_ext = await get_extended_analysis(extended)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        generate_extended_pdf(
            name=name,
            birthdate=birthdate,
            extended=extended,
            analysis_ext=ai_ext,
            output_path=tmp.name
        )

        with open(tmp.name, "rb") as pdf_file:
            await update.message.reply_document(
                document=pdf_file,
                filename="extended_profile_report.pdf",
                caption="📘 Ваш отчёт по расширенным числам"
            )

    await update.message.reply_text(
        "Выберите следующий шаг:",
        reply_markup=build_after_analysis_keyboard()
    )

    return ConversationHandler.END
