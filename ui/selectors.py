from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes

from ui import build_year_keyboard

SELECT_YEAR, SELECT_MONTH = range(2)


async def ask_year(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📆 Выберите год:", reply_markup=build_year_keyboard())
    return SELECT_YEAR


async def ask_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        await update.message.reply_text("❗️Ожидалась кнопка. Пожалуйста, выберите год.")
        return SELECT_MONTH

    await query.answer()

    if query.data.startswith("cal_year_"):
        selected_year = int(query.data.replace("cal_year_", ""))
    else:
        await query.message.reply_text("⚠️ Некорректный формат года.")
        return SELECT_MONTH

    context.user_data["selected_year"] = selected_year

    keyboard = [
        [InlineKeyboardButton(str(i + 1), callback_data=str(i + 1))] for i in range(12)
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("📅 Теперь выберите месяц:", reply_markup=reply_markup)
    return SELECT_MONTH


# Текстовые подсказки для сценария «Календарь дней»
ASK_DAYS_YEAR_PROMPT = "📅 Введите *год* (например, 2025)."
ASK_DAYS_MONTH_PROMPT = (
    "🗓 Теперь введите *месяц* числом от 1 до 12 (например, 8).\n"
    "Можно также словами: январь, февраль, ... (регистр не важен)."
)
ASK_DAYS_MONTHYEAR_PROMPT = (
    "📅 Введите месяц и год в формате *MM.YYYY* — например, 08.2025\n"
    "Также подойдёт: 8.2025, 2025-08, 2025/8"
)
