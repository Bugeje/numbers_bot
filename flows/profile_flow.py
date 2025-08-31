# flows/profile_flow_refactored.py
"""
Рефакторинг flow ядра личности с использованием базового класса.
Устраняет дублирование кода.
"""
from typing import Dict, Any, Optional, Callable
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from intelligence import get_ai_analysis
from calc import calculate_core_profile
from output import generate_core_pdf
from helpers import (
    M, FILENAMES, MessageManager, normalize_name, 
    parse_and_normalize
)
from interface import build_after_analysis_keyboard
from helpers.pdf_flow_base import BasePDFFlow, StandardDataValidationMixin, AIAnalysisMixin
from .states import State


class CoreProfileFlow(BasePDFFlow, StandardDataValidationMixin, AIAnalysisMixin):
    """Рефакторинг core profile flow с использованием базового класса."""
    
    def __init__(self):
        super().__init__(FILENAMES.CORE_PROFILE, requires_ai=True)
    
    async def validate_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Валидация данных для core profile."""
        if not await self.validate_basic_profile_data(update, context):
            return State.ASK_BIRTHDATE
        return ConversationHandler.END
    
    async def perform_ai_analysis(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """AI анализ для core profile."""
        # Используем стандартный AI анализ который будет обработан базовым классом
        profile = context.user_data["core_profile"]
        analysis = await self.safe_ai_analysis(get_ai_analysis, profile)
        
        return analysis
    
    async def generate_pdf_data(self, context: ContextTypes.DEFAULT_TYPE, ai_analysis: Optional[str]) -> Dict[str, Any]:
        """Подготовка данных для генерации core PDF."""
        return {
            "name": context.user_data["name"],
            "birthdate": context.user_data["birthdate"],
            "profile": context.user_data["core_profile"],
            "analysis": ai_analysis or M.ERRORS.AI_GENERIC,
            "output_path": ""  # Will be set by the base class
        }
    
    def get_pdf_generator(self) -> Callable:
        """Возвращает функцию генерации core PDF."""
        return generate_core_pdf


# Экземпляр flow для использования
core_profile_flow = CoreProfileFlow()


async def show_core_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Считает и показывает числа ядра личности без ИИ."""
    # --- validate name ---
    try:
        name = normalize_name(context.user_data.get("name"))
    except Exception as e:
        await update.effective_message.reply_text(
            f"{M.ERRORS.NAME_PREFIX}{e}\n\n{M.HINTS.ASK_NAME_FULL}"
        )
        return State.ASK_NAME

    # --- validate birthdate ---
    raw_birthdate = (
        update.message.text.strip() if update.message else context.user_data.get("birthdate")
    )
    try:
        birthdate = parse_and_normalize(raw_birthdate)
        # защита от будущей даты
        try:
            dt = datetime.strptime(birthdate, "%d.%m.%Y")
            if dt.date() > datetime.now().date():
                raise ValueError(M.ERRORS.DATE_FUTURE)
        except ValueError:
            pass
    except Exception as e:
        await update.effective_message.reply_text(
            f"{M.ERRORS.DATE_PREFIX}{e}\n\n{M.DATE_FORMATS_NOTE}\n{M.HINTS.ASK_BIRTHDATE_COMPACT}"
        )
        return State.ASK_BIRTHDATE

    # сохранить данные
    context.user_data["birthdate"] = birthdate

    # --- calculate core profile ---
    try:
        profile = calculate_core_profile(name, birthdate)
        context.user_data["core_profile"] = profile
    except Exception as e:
        await M.send_auto_delete_error(update, context, M.format_error_details(M.ERRORS.CALC_PROFILE, str(e)))
        return ConversationHandler.END

    # --- показать итог и навигацию ---
    msg_manager = MessageManager(context)
    
    await update.effective_message.reply_text(
        M.format_core_summary(name, birthdate, profile), parse_mode="Markdown"
    )
    
    await msg_manager.send_navigation_message(
        update, M.HINTS.NEXT_STEP, reply_markup=build_after_analysis_keyboard()
    )

    return State.EXTENDED_ANALYSIS


async def core_profile_ai_and_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ИИ-анализ и PDF — использует рефакторинг базового класса."""
    # Check if core profile already exists to prevent double generation
    if "core_profile" not in context.user_data:
        # If core profile doesn't exist, we need to generate it first
        # This shouldn't normally happen, but let's handle it gracefully
        try:
            name = normalize_name(context.user_data.get("name"))
            birthdate = context.user_data.get("birthdate")
            if name and birthdate:
                profile = calculate_core_profile(name, birthdate)
                context.user_data["core_profile"] = profile
            else:
                await M.send_auto_delete_error(update, context, M.HINTS.MISSING_BASIC_DATA)
                return ConversationHandler.END
        except Exception as e:
            await M.send_auto_delete_error(update, context, M.format_error_details(M.ERRORS.CALC_PROFILE, str(e)))
            return ConversationHandler.END
    
    return await core_profile_flow.execute(update, context)