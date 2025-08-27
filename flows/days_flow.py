import tempfile

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters

from intelligence import get_active_components, get_calendar_analysis
from calc.cycles import generate_calendar_matrix, get_personal_month
from output import generate_pdf, mark_calendar_cells
from interface import ASK_DAYS_MONTHYEAR_PROMPT, SELECT_MONTH, build_after_analysis_keyboard
from helpers import M, MessageManager, Progress, action_typing, action_upload, RU_MONTHS_FULL, parse_month_year, run_blocking

from .base import start


async def ask_days_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Очищаем предыдущие навигационные сообщения
    msg_manager = MessageManager(context)
    await msg_manager.cleanup_tracked_messages()
    
    # очистим хвосты
    for k in ("year", "month", "days_year", "days_month"):
        context.user_data.pop(k, None)

    await msg_manager.send_and_track(update, ASK_DAYS_MONTHYEAR_PROMPT, parse_mode="Markdown")
    return SELECT_MONTH


async def receive_days_monthyear_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Очищаем промпт о вводе месяца/года
    msg_manager = MessageManager(context)
    await msg_manager.cleanup_tracked_messages()
    
    try:
        month, year = parse_month_year(update.message.text)
        context.user_data["month"] = month
        context.user_data["year"] = year
        context.user_data["days_month"] = month
        context.user_data["days_year"] = year
        return await send_days_pdf(update, context)
    except Exception as e:
        await update.message.reply_text(
            f"❌ {e}\n{ASK_DAYS_MONTHYEAR_PROMPT}", parse_mode="Markdown"
        )
        return SELECT_MONTH


async def send_days_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Генерация PDF с календарём дней на выбранный месяц."""
    year = int(context.user_data.get("year", 0))
    month = int(context.user_data.get("month", 0))
    name = context.user_data.get("name")
    birthdate = context.user_data.get("birthdate")
    profile = context.user_data.get("core_profile")

    if not (year and month and name and birthdate and profile):
        await update.effective_message.reply_text(
            "⚠️ Не хватает данных для расчёта. Пожалуйста, начните заново."
        )
        return ConversationHandler.END

    # --- прогресс: расчёты ---
    await action_typing(update.effective_chat)
    progress = await Progress.start(update, f"📅 Готовлю календарь дней на {RU_MONTHS_FULL[month]} {year}...")

    personal_month = get_personal_month(birthdate, year, month)
    context.user_data["personal_month"] = personal_month

    calendar = generate_calendar_matrix(birthdate, year=year, month=month)
    calendar, matches_by_day = mark_calendar_cells(calendar, profile)
    single_components, gradients, fusion_groups = get_active_components(matches_by_day)

    legend = {
        "match-life_path": "🟥 Жизненный путь — тема предназначения, судьбоносные акценты",
        "match-expression": "🟦 Выражение — энергия действия, реализация потенциала",
        "match-soul": "🟣 Душа — внутренние желания и эмоциональные импульсы",
        "match-personality": "🟨 Личность — стиль поведения, как вас видят окружающие",
        "match-birthday": "🟩 День рождения — врождённые дары, проявления спонтанности",
    }
    gradient_descriptions = [legend.get(g, g) for g in gradients if g in legend]

    month_name = f"{RU_MONTHS_FULL[month]} {year}"

    # --- прогресс: ИИ-анализ ---
    await progress.set("🤖 Генерирую AI-анализ календаря...")

    try:
        calendar_text = await get_calendar_analysis(
            profile=profile,
            month_name=month_name,
            matches_by_day=matches_by_day,
            single_components=single_components,
            gradients=gradient_descriptions,
            fusion_groups=fusion_groups,
            personal_month=personal_month,
        )
        if isinstance(calendar_text, str) and calendar_text.startswith("❌"):
            calendar_text = M.ERRORS.AI_GENERIC
    except Exception:
        calendar_text = M.ERRORS.AI_GENERIC

    emoji_to_html = {
        "🟥": '<span style="display:inline-block; width:14px; height:14px; background-color:#e74c3c; border-radius:2px; margin:0 2px;"></span>',
        "🟦": '<span style="display:inline-block; width:14px; height:14px; background-color:#3498db; border-radius:2px; margin:0 2px;"></span>',
        "🟣": '<span style="display:inline-block; width:14px; height:14px; background-color:#9b59b6; border-radius:2px; margin:0 2px;"></span>',
        "🟨": '<span style="display:inline-block; width:14px; height:14px; background-color:#f39c12; border-radius:2px; margin:0 2px;"></span>',
        "🟩": '<span style="display:inline-block; width:14px; height:14px; background-color:#2ecc71; border-radius:2px; margin:0 2px;"></span>',
    }

    for emoji, html in emoji_to_html.items():
        calendar_text = calendar_text.replace(emoji, html)

    # --- прогресс: PDF ---
    await progress.set(M.PROGRESS.PDF_ONE)
    await action_upload(update.effective_chat)

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            await run_blocking(
                generate_pdf,
                name=name,
                birthdate=birthdate,
                profile=profile,
                filename=tmp.name,
                personal_calendar=calendar,
                calendar_month=str(month),
                calendar_year=str(year),
                calendar_text=calendar_text,
            )
            
            await progress.set(M.PROGRESS.SENDING_ONE)
            await action_upload(update.effective_chat)
            
            with open(tmp.name, "rb") as pdf_file:
                await update.message.reply_document(
                    document=pdf_file, 
                    filename="Календарь_дней.pdf",
                    caption="📅 Ваш персональный календарь дней"
                )

        await progress.finish()
    except Exception:
        await progress.fail(M.ERRORS.PDF_FAIL)

    # Отправляем новое навигационное сообщение (трекаем)
    msg_manager = MessageManager(context)
    await msg_manager.send_and_track(
        update, M.HINTS.NEXT_STEP, reply_markup=build_after_analysis_keyboard()
    )

    return ConversationHandler.END


days_conversation_handler = ConversationHandler(
    entry_points=[
        MessageHandler(filters.Regex("📅 Календарь дней"), ask_days_start),
    ],
    states={
        SELECT_MONTH: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_days_monthyear_text),
        ],
    },
    fallbacks=[MessageHandler(filters.Regex("^🔁 Старт$"), start)],
)
