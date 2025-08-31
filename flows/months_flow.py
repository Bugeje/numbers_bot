# flows/months_flow_refactored.py
"""
Рефакторинг months flow с использованием базового класса.
Устраняет дублирование кода.
"""
import re
from typing import Dict, Any, Optional, Callable
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters

from calc.cycles import MONTH_NAMES, generate_personal_month_cycle_table, calculate_personal_year
from calc import calculate_core_profile
from intelligence import get_months_year_analysis
from output import create_months_year_report_pdf
from interface import ASK_MONTHS_YEAR_PROMPT, SELECT_MONTHS_YEAR
from helpers import M, MessageManager, FILENAMES, BTN
from helpers.data_validator import DataValidator
from helpers.pdf_flow_base import BasePDFFlow, StandardDataValidationMixin, AIAnalysisMixin
from interface import build_after_analysis_keyboard
from .base import start


class MonthsFlow(BasePDFFlow, StandardDataValidationMixin, AIAnalysisMixin):
    """Рефакторинг months flow с использованием базового класса."""
    
    def __init__(self):
        super().__init__(FILENAMES.MONTHS, requires_ai=True)
    
    async def validate_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Валидация данных для months analysis."""
        user_data = context.user_data
        name = user_data.get("name")
        birthdate = user_data.get("birthdate")
        core_profile = user_data.get("core_profile")
        target_year = user_data.get("months_target_year")

        # Use DataValidator for basic profile validation
        success, validated_data = await DataValidator.validate_basic_profile(update, context)
        if not success:
            return ConversationHandler.END

        if not target_year:
            await M.send_auto_delete_error(update, context, M.HINTS.MISSING_YEAR)
            return ConversationHandler.END

        # Автоматически рассчитываем core_profile, если его нет
        if not core_profile:
            try:
                core_profile = calculate_core_profile(name, birthdate)
                user_data["core_profile"] = core_profile
            except Exception as e:
                await M.send_auto_delete_error(update, context, M.format_error_details(M.ERRORS.CALC_PROFILE, str(e)))
                return ConversationHandler.END

        # Вычисляем персональный год для выбранного года
        try:
            personal_year_str = calculate_personal_year(birthdate, target_year)
            personal_year = int(personal_year_str.split('(')[0])  # Извлекаем базовое число
            
            # Получаем таблицу месяцев для данного персонального года
            raw_month_cycles = generate_personal_month_cycle_table()
            months_data = [str(raw_month_cycles[personal_year][m]) for m in MONTH_NAMES]
            month_cycles = {str(k): [str(v[m]) for m in MONTH_NAMES] for k, v in raw_month_cycles.items()}
            
            # Сохраняем вычисленные данные
            user_data["months_data"] = months_data
            user_data["month_cycles"] = month_cycles
            user_data["personal_year"] = personal_year
            user_data["target_year"] = target_year
        except Exception as e:
            await M.send_auto_delete_error(update, context, f"{M.ERRORS.CALC_PROFILE}\n{str(e)}")
            return ConversationHandler.END
            
        return ConversationHandler.END
    
    async def perform_ai_analysis(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """AI анализ для months."""
        progress = await self.start_ai_progress(update)
        
        user_data = context.user_data
        analysis = await self.safe_ai_analysis(
            get_months_year_analysis,
            profile=user_data["core_profile"],
            birthdate=user_data["birthdate"],
            personal_year=user_data["personal_year"],
            year=user_data["target_year"],
        )
        
        return analysis
    
    async def generate_pdf_data(self, context: ContextTypes.DEFAULT_TYPE, ai_analysis: Optional[str]) -> Dict[str, Any]:
        """Подготовка данных для генерации months PDF."""
        user_data = context.user_data
        return {
            "name": user_data["name"],
            "birthdate": user_data["birthdate"],
            "target_year": user_data["target_year"],
            "personal_year": user_data["personal_year"],
            "months_data": user_data["months_data"],
            "core_profile": user_data["core_profile"],
            "ai_analysis": ai_analysis or M.ERRORS.AI_GENERIC,
            "output_path": ""  # Will be set by the base class
        }
    
    def get_pdf_generator(self) -> Callable:
        """Возвращает функцию генерации months PDF."""
        return create_months_year_report_pdf


# Экземпляр flow для использования
months_flow = MonthsFlow()


async def ask_months_year_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запрос года для анализа месяцев."""
    # Очищаем предыдущие навигационные сообщения
    msg_manager = MessageManager(context)
    await msg_manager.cleanup_tracked_messages()
    
    # очистим хвосты
    for k in ("months_target_year",):
        context.user_data.pop(k, None)

    await msg_manager.send_and_track(update, ASK_MONTHS_YEAR_PROMPT, parse_mode="Markdown")
    return SELECT_MONTHS_YEAR


async def receive_months_year_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ввода года для анализа месяцев."""
    # Extract the year from the user's message
    try:
        year_text = update.message.text.strip()
        # Try to parse the year - handle both full years (2025) and short years (25)
        if len(year_text) == 2:
            # Convert 2-digit year to 4-digit (assuming 20xx for 00-29, 19xx for 30-99)
            year_int = int(year_text)
            if year_int < 30:
                year_int += 2000
            else:
                year_int += 1900
        elif len(year_text) == 4:
            year_int = int(year_text)
        else:
            # Try to extract a 4-digit year from the text
            import re
            match = re.search(r'\b(19|20)\d{2}\b', year_text)
            if match:
                year_int = int(match.group(0))
            else:
                raise ValueError("Некорректный формат года")
        
        # Validate year range (reasonable range)
        current_year = datetime.now().year
        if year_int < 1900 or year_int > current_year + 5:
            raise ValueError(f"Год должен быть в диапазоне 1900-{current_year + 5}")
            
        context.user_data["months_target_year"] = year_int
    except (ValueError, AttributeError) as e:
        await M.send_auto_delete_error(update, context, f"{M.ERRORS.DATE_PREFIX}Некорректный год: {str(e)}")
        return SELECT_MONTHS_YEAR
    
    return await send_months_pdf(update, context)


async def send_months_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Генерация месяцев — использует рефакторинг базового класса."""
    return await months_flow.execute(update, context)


months_conversation_handler = ConversationHandler(
    entry_points=[
        MessageHandler(filters.Regex(f"^{re.escape(BTN.MONTHS)}$"), ask_months_year_start),
    ],
    states={
        SELECT_MONTHS_YEAR: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_months_year_text),
        ],
    },
    fallbacks=[MessageHandler(filters.Regex(f"^{re.escape(BTN.RESTART)}$"), start)],
)