from telegram import Update
from telegram.ext import ContextTypes
from ui import (
    build_year_keyboard,
    build_month_keyboard,
    build_day_keyboard,
    format_date,
    MONTHS
)
from handlers.core_profile import show_core_profile
from handlers.partner import generate_compatibility

from .states import State

async def handle_calendar_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("cal_year_"):
        year = int(data.split("_")[2])
        context.user_data["year"] = year
        await query.edit_message_text(f"📅 Год: {year}\nТеперь выберите месяц:", reply_markup=build_month_keyboard(year))
        return State.ASK_BIRTHDATE

    elif data.startswith("cal_month_"):
        _, _, year, month = data.split("_")
        year = int(year)
        month = int(month)
        context.user_data["year"] = year
        context.user_data["month"] = month
        await query.edit_message_text(f"📅 {MONTHS[month-1]} {year}\nВыберите день:", reply_markup=build_day_keyboard(year, month))
        return State.ASK_BIRTHDATE

    elif data.startswith("cal_day_"):
        _, _, year, month, day = data.split("_")
        year, month, day = int(year), int(month), int(day)
        birthdate_str = format_date(year, month, day)

        if context.user_data.get("selecting_partner"):
            context.user_data["partner_birthdate"] = birthdate_str
            await query.edit_message_text(f"📅 Дата рождения партнёра выбрана: {birthdate_str}")
            return await generate_compatibility(update, context)
        else:
            context.user_data["birthdate"] = birthdate_str
            await query.edit_message_text(f"📅 Дата выбрана: {birthdate_str}")
            return await show_core_profile(update, context)

    elif data == "cal_back_year":
        await query.edit_message_text("📅 Выберите год:", reply_markup=build_year_keyboard())
        return State.ASK_BIRTHDATE

    elif data.startswith("cal_back_month_"):
        year = int(data.split("_")[-1])
        await query.edit_message_text(f"📅 Год: {year}\nВыберите месяц:", reply_markup=build_month_keyboard(year))
        return State.ASK_BIRTHDATE
