import tempfile

from telegram import Update
from telegram.ext import ContextTypes

from calc.cycles import MONTH_NAMES, generate_personal_month_cycle_table
from output import create_months_report_pdf
from interface import build_after_analysis_keyboard
from helpers import run_blocking


async def send_months_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = context.user_data.get("name")
    birthdate = context.user_data.get("birthdate")

    if not name or not birthdate:
        await update.message.reply_text("⚠️ Сначала введите имя и дату рождения.")
        return

    # Получаем полную таблицу месяцев (1–9)
    raw_month_cycles = generate_personal_month_cycle_table()
    month_cycles = {str(k): [str(v[m]) for m in MONTH_NAMES] for k, v in raw_month_cycles.items()}

    # Генерация PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        await run_blocking(create_months_report_pdf, name, birthdate, month_cycles, tmp.name)

        await update.message.reply_document(
            document=open(tmp.name, "rb"), filename="Анализ_месяцев.pdf"
        )

    await update.message.reply_text(
        "Выберите следующий шаг:", reply_markup=build_after_analysis_keyboard()
    )
