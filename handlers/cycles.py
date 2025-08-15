from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from numerology.cycles import (
    generate_personal_year_table,
    calculate_pinnacles_with_periods,
    split_years_by_pinnacles,
)
from reports import generate_cycles_pdf
from ui import build_after_analysis_keyboard
from utils import run_blocking


async def show_cycles_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        name = context.user_data["name"]
        birthdate = context.user_data["birthdate"]
        life_path = context.user_data["core_profile"]["life_path"]

        await update.message.reply_text("🔄 Готовлю анализ по циклам и годам...")

        # Вычисления
        personal_years = generate_personal_year_table(birthdate)
        pinnacles = calculate_pinnacles_with_periods(birthdate, life_path)
        personal_year_blocks = split_years_by_pinnacles(birthdate)

        # Генерация PDF
        pdf_path = await run_blocking(
            generate_cycles_pdf, 
            name, 
            birthdate, 
            personal_years, 
            pinnacles, 
            personal_year_blocks
        )

        with open(pdf_path, "rb") as f:
            await update.message.reply_document(document=f, filename="cycles.pdf")

        # Меню выбора следующего действия
        await update.message.reply_text(
            "Выберите следующий шаг:",
            reply_markup=build_after_analysis_keyboard()
        )

        return ConversationHandler.END

    except Exception as e:
        await update.message.reply_text("❌ Произошла ошибка при формировании анализа циклов.")
        raise e
