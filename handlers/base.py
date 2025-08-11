from handlers.states import State
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from ui import build_year_keyboard
from .states import State


START_KEYBOARD = ReplyKeyboardMarkup(
    [[KeyboardButton("🔁 Старт")]],
    resize_keyboard=True,
    one_time_keyboard=True
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "Привет! Я помогу рассчитать твоё ядро личности по нумерологии.\n\nКак тебя зовут (фамилия и имя)?",
        reply_markup=START_KEYBOARD
    )
    return State.State.ASK_NAME

async def save_name_and_ask_birthdate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text.strip()
    await update.message.reply_text("📅 Выберите год рождения:", reply_markup=build_year_keyboard())
    return State.State.ASK_BIRTHDATE