# flows/extended_flow_refactored.py
"""
Рефакторинг extended flow с использованием базового класса.
Устраняет дублирование кода.
"""
from typing import Dict, Any, Optional, Callable
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from intelligence import get_extended_analysis
from calc.extended import calculate_extended_profile
from output import generate_extended_pdf
from helpers import M, FILENAMES, MessageManager
from helpers.pdf_flow_base import BasePDFFlow, StandardDataValidationMixin, AIAnalysisMixin
from interface import build_after_analysis_keyboard
from .states import State


class ExtendedProfileFlow(BasePDFFlow, StandardDataValidationMixin, AIAnalysisMixin):
    """Рефакторинг extended profile flow с использованием базового класса."""
    
    def __init__(self):
        super().__init__(FILENAMES.EXTENDED_PROFILE, requires_ai=True)
    
    async def validate_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Валидация данных для extended profile."""
        user_data = context.user_data
        name = user_data.get("name")
        birthdate = user_data.get("birthdate")
        core_profile = user_data.get("core_profile")

        if not (name and birthdate and core_profile):
            await M.send_auto_delete_error(update, context, M.HINTS.MISSING_BASIC_DATA)
            return ConversationHandler.END
        
        # Расчёт расширенных чисел
        try:
            extended = calculate_extended_profile(name, birthdate)
            context.user_data["extended_profile"] = extended
        except Exception as e:
            await M.send_auto_delete_error(update, context, f"{M.ERRORS.CALC_PROFILE}\n{str(e)}")
            return ConversationHandler.END
            
        return ConversationHandler.END
    
    async def perform_ai_analysis(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """AI анализ для extended profile."""
        progress = await self.start_ai_progress(update)
        
        extended = context.user_data["extended_profile"]
        analysis = await self.safe_ai_analysis(get_extended_analysis, extended)
        
        return analysis
    
    async def generate_pdf_data(self, context: ContextTypes.DEFAULT_TYPE, ai_analysis: Optional[str]) -> Dict[str, Any]:
        """Подготовка данных для генерации extended PDF."""
        return {
            "name": context.user_data["name"],
            "birthdate": context.user_data["birthdate"],
            "extended": context.user_data["extended_profile"],
            "analysis_ext": ai_analysis or M.ERRORS.AI_GENERIC
        }
    
    def get_pdf_generator(self) -> Callable:
        """Возвращает функцию генерации extended PDF."""
        return generate_extended_pdf


# Экземпляр flow для использования
extended_profile_flow = ExtendedProfileFlow()


async def show_extended_only_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Расширенный анализ — использует рефакторинг базового класса."""
    return await extended_profile_flow.execute(update, context)