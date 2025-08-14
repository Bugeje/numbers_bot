from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from numerology import calculate_core_profile
from ai import get_compatibility_interpretation
from ui import build_year_keyboard, build_after_analysis_keyboard
from reports import generate_partner_pdf
from utils import run_blocking
import tempfile

from .states import State


async def request_partner_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["selecting_partner"] = True
    await update.message.reply_text("Введите имя и фамилию второго партнёра:")
    return State.ASK_PARTNER_NAME


async def save_partner_name_and_ask_birthdate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("selecting_partner"):
        return
    
    context.user_data["partner_name"] = update.message.text.strip()
    await update.message.reply_text("📅 Выберите дату рождения партнёра:", reply_markup=build_year_keyboard())
    return State.ASK_PARTNER_BIRTHDATE


async def generate_compatibility(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        name_a = context.user_data["name"]
        birth_a = context.user_data["birthdate"]
        profile_a = context.user_data["core_profile"]

        name_b = context.user_data["partner_name"]
        birth_b = context.user_data.get("partner_birthdate")

        if not birth_b and update.message:
            birth_b = update.message.text.strip()
            context.user_data["partner_birthdate"] = birth_b
        elif not birth_b:
            await update.effective_message.reply_text("❌ Не удалось получить дату рождения партнёра.")
            return ConversationHandler.END

        profile_b = calculate_core_profile(name_b, birth_b)
        await update.effective_message.reply_text("🔄 Получаю AI-анализ совместимости, подождите...")

        interpretation = await get_compatibility_interpretation(profile_a, profile_b)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            await run_blocking(
                generate_partner_pdf,
                name_a, birth_a, profile_a,
                name_b, birth_b, profile_b,
                interpretation=interpretation,
                output_path=tmp.name
            )
            await update.effective_message.reply_document(
                open(tmp.name, "rb"),
                filename="Совместимость_партнёров.pdf"
            )

        context.user_data.pop("selecting_partner", None)

        await update.effective_message.reply_text(
            "Выберите следующий шаг:",
            reply_markup=build_after_analysis_keyboard()
        )

        return ConversationHandler.END

    except Exception as e:
        await update.effective_message.reply_text(f"❌ Ошибка: {e}")
        return ConversationHandler.END
