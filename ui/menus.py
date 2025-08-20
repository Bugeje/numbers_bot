from telegram import ReplyKeyboardMarkup, KeyboardButton
from utils import BTN

def build_after_analysis_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BTN.CORE), KeyboardButton(BTN.PARTNER)],
            [KeyboardButton(BTN.EXTENDED), KeyboardButton(BTN.BRIDGES)],
            [KeyboardButton(BTN.CYCLES), KeyboardButton(BTN.MONTHS)],
            [KeyboardButton(BTN.CALENDAR_DAYS)],
            [KeyboardButton(BTN.RESTART)],
        ],
        resize_keyboard=True
    )
