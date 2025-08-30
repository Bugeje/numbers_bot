# flows/bridges_flow_refactored.py
"""
Рефакторинг bridges flow с использованием базового класса.
Устраняет дублирование кода.
"""
from typing import Dict, Any, Optional, Callable

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from intelligence import get_bridges_analysis
from calc.extended import calculate_bridges
from output import generate_bridges_pdf
from helpers import M, FILENAMES, MessageManager
from helpers.pdf_flow_base import BasePDFFlow, StandardDataValidationMixin, AIAnalysisMixin
from interface import build_after_analysis_keyboard
from .states import State


class BridgesFlow(BasePDFFlow, StandardDataValidationMixin, AIAnalysisMixin):
    """Рефакторинг bridges flow с использованием базового класса."""
    
    def __init__(self):
        super().__init__(FILENAMES.BRIDGES, requires_ai=True)
    
    async def validate_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Валидация данных для bridges."""
        user_data = context.user_data
        name = user_data.get("name")
        birthdate = user_data.get("birthdate")
        core_profile = user_data.get("core_profile")

        # ядро обязательно
        if not (name and birthdate and core_profile):
            await M.send_auto_delete_error(update, context, M.HINTS.MISSING_BASIC_DATA)
            return ConversationHandler.END

        # если мосты ещё не считались — посчитаем сейчас
        bridges = user_data.get("bridges")
        if not bridges:
            try:
                bridges = calculate_bridges(core_profile)
                user_data["bridges"] = bridges
            except Exception as e:
                await M.send_auto_delete_error(update, context, f"{M.ERRORS.CALC_PROFILE}\n{M.HINTS.CALC_CORE_FIRST}")
                return ConversationHandler.END
                
        return ConversationHandler.END
    
    async def perform_ai_analysis(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """AI анализ для bridges."""
        progress = await self.start_ai_progress(update)
        
        bridges = context.user_data["bridges"]
        analysis = await self.safe_ai_analysis(get_bridges_analysis, bridges)
        
        return analysis
    
    async def generate_pdf_data(self, context: ContextTypes.DEFAULT_TYPE, ai_analysis: Optional[str]) -> Dict[str, Any]:
        """Подготовка данных для генерации bridges PDF."""
        return {
            "name": context.user_data["name"],
            "birthdate": context.user_data["birthdate"],
            "bridges": context.user_data["bridges"],
            "analysis_bridges": ai_analysis or M.ERRORS.AI_GENERIC,
            "output_path": ""  # Will be set by the base class
        }
    
    def get_pdf_generator(self) -> Callable:
        """Возвращает функцию генерации bridges PDF."""
        return generate_bridges_pdf


# Экземпляр flow для использования
bridges_flow = BridgesFlow()


async def send_bridges_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Мосты — использует рефакторинг базового класса."""
    return await bridges_flow.execute(update, context)