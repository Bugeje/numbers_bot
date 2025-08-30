# flows/days_flow_refactored.py
"""
Рефакторинг days flow с использованием базового класса.
Устраняет дублирование кода.
"""
import re
from typing import Dict, Any, Optional, Callable

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters

from intelligence import get_active_components, get_calendar_analysis
from calc.cycles import generate_calendar_matrix, get_personal_month
from output import generate_pdf, mark_calendar_cells
from interface import ASK_DAYS_MONTHYEAR_PROMPT, SELECT_MONTH
from helpers import M, MessageManager, RU_MONTHS_FULL, parse_month_year, FILENAMES, BTN
from helpers.pdf_flow_base import BasePDFFlow, StandardDataValidationMixin, AIAnalysisMixin
from interface import build_after_analysis_keyboard
from .base import start


class DaysFlow(BasePDFFlow, StandardDataValidationMixin, AIAnalysisMixin):
    """Рефакторинг days flow с использованием базового класса."""
    
    def __init__(self):
        super().__init__(FILENAMES.CALENDAR_DAYS, requires_ai=True)
    
    async def validate_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Валидация данных для days analysis."""
        user_data = context.user_data
        year = int(user_data.get("year", 0))
        month = int(user_data.get("month", 0))
        name = user_data.get("name")
        birthdate = user_data.get("birthdate")
        profile = user_data.get("core_profile")

        if not (year and month and name and birthdate and profile):
            await M.send_auto_delete_error(update, context, M.HINTS.MISSING_DATA)
            return ConversationHandler.END

        # Вычисляем данные календаря
        try:
            personal_month = get_personal_month(birthdate, year, month)
            calendar = generate_calendar_matrix(birthdate, year=year, month=month)
            calendar, matches_by_day = mark_calendar_cells(calendar, profile)
            single_components, gradients, fusion_groups = get_active_components(matches_by_day)

            legend = {
                "match-life_path": M.CALENDAR_LEGENDS.LIFE_PATH,
                "match-expression": M.CALENDAR_LEGENDS.EXPRESSION,
                "match-soul": M.CALENDAR_LEGENDS.SOUL,
                "match-personality": M.CALENDAR_LEGENDS.PERSONALITY,
                "match-birthday": M.CALENDAR_LEGENDS.BIRTHDAY,
            }
            gradient_descriptions = [legend.get(g, g) for g in gradients if g in legend]

            month_name = f"{RU_MONTHS_FULL[month]} {year}"
            
            # Сохраняем вычисленные данные
            user_data["personal_month"] = personal_month
            user_data["calendar"] = calendar
            user_data["matches_by_day"] = matches_by_day
            user_data["single_components"] = single_components
            user_data["gradients"] = gradients
            user_data["fusion_groups"] = fusion_groups
            user_data["gradient_descriptions"] = gradient_descriptions
            user_data["month_name"] = month_name
        except Exception as e:
            await M.send_auto_delete_error(update, context, f"{M.ERRORS.CALC_PROFILE}\n{str(e)}")
            return ConversationHandler.END
            
        return ConversationHandler.END
    
    async def perform_ai_analysis(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """AI анализ для days."""
        progress = await self.start_ai_progress(update)
        
        user_data = context.user_data
        analysis = await self.safe_ai_analysis(
            get_calendar_analysis,
            profile=user_data["core_profile"],
            month_name=user_data["month_name"],
            matches_by_day=user_data["matches_by_day"],
            single_components=user_data["single_components"],
            gradients=user_data["gradient_descriptions"],
            fusion_groups=user_data["fusion_groups"],
            personal_month=user_data["personal_month"],
        )
        
        # Обработка эмодзи в анализе
        emoji_to_html = {
            "🟥": '<span style="display:inline-block; width:14px; height:14px; background-color:#e74c3c; border-radius:2px; margin:0 2px;"></span>',
            "🟦": '<span style="display:inline-block; width:14px; height:14px; background-color:#3498db; border-radius:2px; margin:0 2px;"></span>',
            "🟣": '<span style="display:inline-block; width:14px; height:14px; background-color:#9b59b6; border-radius:2px; margin:0 2px;"></span>',
            "🟨": '<span style="display:inline-block; width:14px; height:14px; background-color:#f39c12; border-radius:2px; margin:0 2px;"></span>',
            "🟩": '<span style="display:inline-block; width:14px; height:14px; background-color:#2ecc71; border-radius:2px; margin:0 2px;"></span>',
        }

        for emoji, html in emoji_to_html.items():
            analysis = analysis.replace(emoji, html)
            
        return analysis
    
    async def generate_pdf_data(self, context: ContextTypes.DEFAULT_TYPE, ai_analysis: Optional[str]) -> Dict[str, Any]:
        """Подготовка данных для генерации days PDF."""
        user_data = context.user_data
        return {
            "name": user_data["name"],
            "birthdate": user_data["birthdate"],
            "profile": user_data["core_profile"],
            "filename": user_data["output_path"],  # Будет установлено в generate_and_send_pdf
            "personal_calendar": user_data["calendar"],
            "calendar_month": str(user_data["month"]),
            "calendar_year": str(user_data["year"]),
            "calendar_text": ai_analysis or M.ERRORS.AI_GENERIC,
        }
    
    def get_pdf_generator(self) -> Callable:
        """Возвращает функцию генерации days PDF."""
        return generate_pdf


# Экземпляр flow для использования
days_flow = DaysFlow()


async def ask_days_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запрос месяца/года для анализа дней."""
    # Очищаем предыдущие навигационные сообщения
    msg_manager = MessageManager(context)
    await msg_manager.cleanup_tracked_messages()
    
    # очистим хвосты
    for k in ("year", "month", "days_year", "days_month"):
        context.user_data.pop(k, None)

    await msg_manager.send_and_track(update, ASK_DAYS_MONTHYEAR_PROMPT, parse_mode="Markdown")
    return SELECT_MONTH


async def receive_days_monthyear_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ввода месяца/года для анализа дней."""
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
        await M.send_auto_delete_error(
            update, context,
            f"{M.ERRORS.DATE_PREFIX}{e}\n{ASK_DAYS_MONTHYEAR_PROMPT}", 
            parse_mode="Markdown"
        )
        return SELECT_MONTH


async def send_days_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Генерация дней — использует рефакторинг базового класса."""
    return await days_flow.execute(update, context)


days_conversation_handler = ConversationHandler(
    entry_points=[
        MessageHandler(filters.Regex(f"^{re.escape(BTN.CALENDAR_DAYS)}$"), ask_days_start),
    ],
    states={
        SELECT_MONTH: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_days_monthyear_text),
        ],
    },
    fallbacks=[MessageHandler(filters.Regex(f"^{re.escape(BTN.RESTART)}$"), start)],
)