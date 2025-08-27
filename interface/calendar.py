from calendar import monthrange

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

MONTHS = ["Янв", "Фев", "Мар", "Апр", "Май", "Июн", "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"]


def build_year_keyboard(start=1950, end=2025):
    keyboard = []
    row = []
    for year in range(start, end + 1):
        row.append(InlineKeyboardButton(str(year), callback_data=f"cal_year_{year}"))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)


def build_month_keyboard(year: int):
    keyboard = []
    for i in range(0, 12, 3):
        row = [
            InlineKeyboardButton(MONTHS[i + j], callback_data=f"cal_month_{year}_{i+j+1}")
            for j in range(3)
        ]
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("⬅ Назад", callback_data="cal_back_year")])
    return InlineKeyboardMarkup(keyboard)


def build_day_keyboard(year: int, month: int):
    _, days_in_month = monthrange(year, month)
    keyboard = []
    row = []
    for day in range(1, days_in_month + 1):
        row.append(InlineKeyboardButton(str(day), callback_data=f"cal_day_{year}_{month}_{day}"))
        if len(row) == 5:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("⬅ Назад", callback_data=f"cal_back_month_{year}")])
    return InlineKeyboardMarkup(keyboard)
