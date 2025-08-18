from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from numerology import calculate_core_profile
from reports import generate_core_pdf
from ai import get_ai_analysis
from ui import build_after_analysis_keyboard
from .states import State
from utils import (
    run_blocking, 
    parse_and_normalize,
    action_typing,
    action_upload,
    PRESETS,
    Progress
)
import tempfile
from datetime import datetime
import asyncio
import re


async def show_core_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # --- validate & normalize name ---
    def _normalize_name(raw: str) -> str:
        s = (raw or "").strip()
        s = re.sub(r"\s+", " ", s)
        if not s:
            raise ValueError("Имя пустое. Введите, например: Анна")
        if len(s) < 2:
            raise ValueError("Имя слишком короткое. Минимум 2 символа.")
        # только буквы (кириллица/латиница), пробел и дефис
        if not re.fullmatch(r"[A-Za-zА-Яа-яЁё\-\s]{2,50}", s):
            raise ValueError("Имя должно содержать только буквы, пробелы и дефис.")
        # Title-Case с сохранением дефисов
        parts = []
        for token in s.split(" "):
            subtokens = [st.capitalize() for st in token.split("-") if st]
            parts.append("-".join(subtokens))
        return " ".join(parts)

    # имя берём из user_data (как и раньше), но валидируем
    try:
        name = _normalize_name(context.user_data.get("name"))
    except Exception as e:
        await update.effective_message.reply_text(f"❌ {e}\n\nВведите имя ещё раз:")
        return State.ASK_NAME

    # --- validate & normalize birthdate ---
    raw_birthdate = update.message.text.strip() if update.message else context.user_data.get("birthdate")
    try:
        birthdate = parse_and_normalize(raw_birthdate)
        # дополнительная проверка: не из будущего
        try:
            # пробуем распарсить в datetime по основному формату,
            # если не получится — считаем, что parse_and_normalize уже нормализовал корректно
            dt = datetime.strptime(birthdate, "%d.%m.%Y")
            if dt.date() > datetime.now().date():
                raise ValueError("Дата рождения не может быть в будущем.")
        except ValueError:
            # игнорируем, если формат не %d.%m.%Y — parse_and_normalize уже проверил диапазоны
            pass
    except Exception as e:
        await update.effective_message.reply_text(
            f"❌ Некорректная дата: {e}\n\nПримеры допустимых форматов: 24.02.1993, 24/02/1993, 1993-02-24, 24-02-1993."
        )
        return State.ASK_BIRTHDATE

    # сохраняем нормализованную дату
    context.user_data["birthdate"] = birthdate

     # старт индикатора
    await action_typing(update.effective_chat)
    progress = await Progress.start(update, PRESETS["calc_core"][0])

    # расчёт ядра + «анимация» этапа
    await progress.animate(PRESETS["calc_core"], delay=0.35)
    try:
        profile = calculate_core_profile(name, birthdate)
        context.user_data["core_profile"] = profile
    except Exception as e:
        await progress.fail("❌ Ошибка при расчёте профиля.")
        await update.effective_message.reply_text(f"Подробности: {e}")
        return ConversationHandler.END

    # --- AI-анализ (мягкая деградация при ошибках сети) ---
    await action_typing(update.effective_chat)
    await progress.animate(PRESETS["ai"], delay=0.6)
    try:
        analysis = await get_ai_analysis(profile)
        if analysis.startswith("❌") or analysis.startswith("[Сетевая ошибка"):
            analysis = "Анализ временно недоступен. Вы можете повторить запрос позже."
    except Exception:
        analysis = "Анализ временно недоступен. Попробуйте позже."
    
    # --- генерация PDF (в отдельном потоке) ---
    await progress.set(PRESETS["pdf"][0])
    await action_upload(update.effective_chat)

    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            output_path = tmp.name

        # WeasyPrint синхронный — выносим из event loop
        await run_blocking(
            generate_core_pdf,
            name=name,
            birthdate=birthdate,
            profile=profile,
            analysis=analysis,
            output_path=output_path
        )

        await progress.set(PRESETS["sending"][0])
        await action_upload(update.effective_chat)

        # отправка PDF
        with open(output_path, "rb") as pdf_file:
            await update.effective_message.reply_document(
                document=pdf_file,
                filename="core_profile_report.pdf",
                caption="📄 Ваш отчёт о ядре личности"
            )

        await progress.finish()  # «✅ Отчёт готов!» + автоудаление

    except Exception as e:
        await update.effective_message.reply_text(
            f"⚠️ Не удалось сформировать PDF: {e}\n"
            f"Я могу прислать текстовый результат без файла."
        )

    # --- следующий шаг для пользователя ---
    await update.effective_message.reply_text(
        "Выберите следующий шаг:",
        reply_markup=build_after_analysis_keyboard()
    )

    return ConversationHandler.END
    

async def send_core_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = context.user_data.get("name")
    birthdate = context.user_data.get("birthdate")
    profile = context.user_data.get("core_profile")

    if not all([name, birthdate, profile]):
        await update.message.reply_text("❌ Не хватает данных для формирования отчёта.")
        return State.EXTENDED_ANALYSIS

    await update.message.reply_text("🤖 Генерирую интерпретацию ядра личности с помощью ИИ, подождите...")

    try:
        interpretation = await get_ai_analysis(profile)
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка при обращении к AI: {e}")
        interpretation = "⚠️ Не удалось получить интерпретацию от ИИ. Пожалуйста, попробуйте позже."

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        await run_blocking(
            generate_core_pdf,
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
