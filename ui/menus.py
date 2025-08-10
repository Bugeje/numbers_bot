from telegram import ReplyKeyboardMarkup, KeyboardButton

def build_after_analysis_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("📄 Ядро личности"), KeyboardButton("💞 Совместимость партнёров")],
            [KeyboardButton("🧩 Расширенные числа"), KeyboardButton("🪄 Мосты")],
            [KeyboardButton("🌀 Циклы и годы"),KeyboardButton("📆 Анализ месяцев")],
            [KeyboardButton("📅 Календарь дней")],
            [KeyboardButton("🔁 Старт")]
        ],
        resize_keyboard=True
    )
