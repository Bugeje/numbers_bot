from telegram import Update
from telegram.ext import ContextTypes
from numerology.cycles import generate_personal_month_cycle_table, MONTH_NAMES
from reports import create_months_report_pdf
from ui import build_after_analysis_keyboard

import tempfile

async def send_months_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = context.user_data.get("name")
    birthdate = context.user_data.get("birthdate")

    if not name or not birthdate:
        await update.message.reply_text("⚠️ Сначала введите имя и дату рождения.")
        return

    # Получаем полную таблицу месяцев (1–9)
    raw_month_cycles = generate_personal_month_cycle_table()
    month_cycles = {
        str(k): [str(v[m]) for m in MONTH_NAMES] for k, v in raw_month_cycles.items()
    }

    # Генерация PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        create_months_report_pdf(name, birthdate, month_cycles, tmp.name)
        await update.message.reply_document(
            document=open(tmp.name, "rb"),
            filename="Анализ_месяцев.pdf"
        )

    await update.message.reply_text(
        "Выберите следующий шаг:",
        reply_markup=build_after_analysis_keyboard()
    )
