# flows/base.py
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes

from helpers import MessageManager, parse_and_normalize, M, BTN

from .profile_flow import show_core_profile
from .states import State

START_KEYBOARD = ReplyKeyboardMarkup(
    [[KeyboardButton(BTN.RESTART)]], resize_keyboard=True, one_time_keyboard=True
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the bot conversation and ask for name."""
    # Создаем MessageManager до очистки user_data
    msg_manager = MessageManager(context)
    
    # Очищаем отслеживаемые сообщения
    await msg_manager.cleanup_tracked_messages()
    
    # Затем очищаем данные пользователя
    context.user_data.clear()
    
    # Создаем новый MessageManager после очистки, чтобы инициализировать пустой список
    msg_manager = MessageManager(context)
    
    await msg_manager.send_and_track(
        update,
        M.HINTS.ASK_NAME_FULL,
        reply_markup=START_KEYBOARD,
    )
    return State.ASK_NAME


async def save_name_and_ask_birthdate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Save user name and ask for birthdate."""
    msg_manager = MessageManager(context)
    await msg_manager.cleanup_tracked_messages()  # Очищаем приветствие
    
    context.user_data["name"] = update.message.text.strip()
    await msg_manager.send_and_track(
        update,
        M.HINTS.ASK_BIRTHDATE_COMPACT
    )
    return State.ASK_BIRTHDATE


async def receive_birthdate_text(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int | object:
    """Receive and validate birthdate text."""
    msg_manager = MessageManager(context)
    
    try:
        date_str = (update.message.text or "").strip()
        normalized = parse_and_normalize(date_str)
        context.user_data["birthdate"] = normalized
        
        # Очищаем сообщение о вводе даты
        await msg_manager.cleanup_tracked_messages()
        
        # переиспользуем существующий сценарий показа профиля
        return await show_core_profile(update, context)
    except Exception as e:
        await M.send_auto_delete_error(update, context, f"{M.ERRORS.DATE_PREFIX}{e}\n{M.HINTS.RETRY_DATE}")
        return State.ASK_BIRTHDATE
