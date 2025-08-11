from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from numerology import calculate_core_profile
from numerology.extended import calculate_bridges
from reports import generate_core_pdf
from ai import get_ai_analysis
from ui import build_after_analysis_keyboard
from .states import State
import tempfile


async def show_core_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = context.user_data.get("name")
    birthdate = update.message.text.strip() if update.message else context.user_data.get("birthdate")
    context.user_data["birthdate"] = birthdate

    try:
        profile = calculate_core_profile(name, birthdate)
        context.user_data["core_profile"] = profile
        
        bridges = calculate_bridges(profile)
        context.user_data["bridges"] = bridges

        title_map = {
            "life_path": "🔢 Число жизненного пути",
            "birthday": "📅 Число дня рождения",
            "expression": "🧬 Число выражения",
            "soul": "💖 Число души",
            "personality": "🎭 Число личности"
        }

        profile_lines = [f"🔹 *Ядро личности для {name}*", f"📆 Дата рождения: {birthdate}", ""]
        for key, title in title_map.items():
            profile_lines.append(f"{title}: {profile[key]}")
        await update.effective_message.reply_text("\n".join(profile_lines), parse_mode="Markdown")

        await update.effective_message.reply_text(
            "🧠 Чтобы получить интерпретацию и PDF-отчёт — нажми одну из кнопок ниже.",
            reply_markup=build_after_analysis_keyboard()
        )

        return State.State.EXTENDED_ANALYSIS

    except Exception as e:
        await update.effective_message.reply_text(f"❌ Ошибка при расчёте: {e}")
        return ConversationHandler.END
    

async def send_core_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = context.user_data.get("name")
    birthdate = context.user_data.get("birthdate")
    profile = context.user_data.get("core_profile")

    if not all([name, birthdate, profile]):
        await update.message.reply_text("❌ Не хватает данных для формирования отчёта.")
        return State.State.EXTENDED_ANALYSIS

    await update.message.reply_text("🤖 Генерирую интерпретацию ядра личности с помощью ИИ, подождите...")

    try:
        interpretation = await get_ai_analysis(profile)
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка при обращении к AI: {e}")
        interpretation = "⚠️ Не удалось получить интерпретацию от ИИ. Пожалуйста, попробуйте позже."

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        generate_core_pdf(
            name=name,
            birthdate=birthdate,
            profile=profile,
            analysis=interpretation,
            output_path=tmp.name
        )

        with open(tmp.name, "rb") as pdf_file:
            await update.message.reply_document(
                document=pdf_file,
                filename="core_profile_report.pdf",
                caption="📄 Ваш отчёт о ядре личности"
            )

    await update.message.reply_text(
        "Выберите следующий шаг:",
        reply_markup=build_after_analysis_keyboard()
    )

    return ConversationHandler.END
