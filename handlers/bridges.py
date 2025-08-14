from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from ai import get_bridges_analysis
from reports import generate_bridges_pdf
from ui import build_after_analysis_keyboard
from utils import run_blocking
import tempfile


async def send_bridges_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    name = user_data.get("name")
    birthdate = user_data.get("birthdate")
    bridges = user_data.get("bridges")

    if not all([name, birthdate, bridges]):
        await update.message.reply_text("❌ Недостаточно данных для PDF отчёта.")
        return ConversationHandler.END

    try:
        analysis = await get_bridges_analysis(bridges)
    except Exception as e:
        await update.message.reply_text(f"Ошибка при анализе мостов: {e}")
        return ConversationHandler.END

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        await run_blocking(
            generate_bridges_pdf,
            name=name,
            birthdate=birthdate,
            bridges=bridges,
            analysis_bridges=analysis,
            output_path=tmp.name
        )

        with open(tmp.name, "rb") as pdf_file:
            await update.message.reply_document(
                document=pdf_file,
                filename="bridges_report.pdf",
                caption="📘 Ваш отчёт по мостам"
            )

    await update.message.reply_text(
        "Выберите следующий шаг:",
        reply_markup=build_after_analysis_keyboard()
    )

    return ConversationHandler.END

