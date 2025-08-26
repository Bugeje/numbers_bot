
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes

from utils import parse_and_normalize

from .core_profile import show_core_profile
from .states import State

START_KEYBOARD = ReplyKeyboardMarkup(
    [[KeyboardButton("🔁 Старт")]], resize_keyboard=True, one_time_keyboard=True
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the bot conversation and ask for name."""
    context.user_data.clear()
    await update.message.reply_text(
        "Привет! Я помогу рассчитать твоё ядро личности по нумерологии.\n\nКак тебя зовут (Фамилия, Имя, Отчество)?",
        reply_markup=START_KEYBOARD,
    )
    return State.ASK_NAME


async def save_name_and_ask_birthdate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Save user name and ask for birthdate."""
    context.user_data["name"] = update.message.text.strip()
    await update.message.reply_text(
        "📅 Введите дату рождения в формате ДД.ММ.ГГГГ (например 24.02.1993)."
        "Можно также 1993-02-24 или 24/02/1993."
    )
    return State.ASK_BIRTHDATE


async def receive_birthdate_text(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int | object:
    """Receive and validate birthdate text."""
    try:
        date_str = (update.message.text or "").strip()
        normalized = parse_and_normalize(date_str)
        context.user_data["birthdate"] = normalized
        # переиспользуем существующий сценарий показа профиля
        return await show_core_profile(update, context)
    except Exception as e:
        await update.message.reply_text(
            f"❌ {e}\nПопробуйте ещё раз. " "Примеры: 24.02.1993, 1993-02-24, 24/02/1993."
        )
        return State.ASK_BIRTHDATE
