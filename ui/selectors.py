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
