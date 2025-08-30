# flows/partner_flow_refactored.py
"""
Рефакторинг partner flow с использованием базового класса.
Устраняет дублирование кода.
"""
from typing import Dict, Any, Optional, Callable

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from intelligence import get_compatibility_interpretation
from calc import calculate_core_profile
from output import generate_partner_pdf
from helpers import M, FILENAMES, MessageManager, parse_and_normalize
from helpers.data_validator import DataValidator
from helpers.pdf_flow_base import BasePDFFlow, StandardDataValidationMixin, AIAnalysisMixin
from interface import build_after_analysis_keyboard
from .states import State


class PartnerFlow(BasePDFFlow, StandardDataValidationMixin, AIAnalysisMixin):
    """Рефакторинг partner flow с использованием базового класса."""
    
    def __init__(self):
        super().__init__(FILENAMES.PARTNER_COMPATIBILITY, requires_ai=True)
    
    async def validate_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Валидация данных для partner compatibility."""
        user_data = context.user_data
        name_a = user_data.get("name")
        birth_a = user_data.get("birthdate")
        profile_a = user_data.get("core_profile")

        name_b = user_data.get("partner_name")
        birth_b = user_data.get("partner_birthdate")

        # Проверяем основные данные пользователя
        if not (name_a and birth_a and profile_a):
            await M.send_auto_delete_error(update, context, M.HINTS.MISSING_BASIC_DATA)
            return ConversationHandler.END

        # Проверяем данные партнера
        if not name_b:
            await M.send_auto_delete_error(update, context, M.HINTS.MISSING_PARTNER_DATA)
            return ConversationHandler.END

        # Валидируем дату рождения партнера, если она еще не валидирована
        if not birth_b and update.message:
            success, validated_birth_b = await DataValidator.validate_birthdate(
                update, context, raw_date=update.message.text.strip()
            )
            if not success:
                return State.ASK_PARTNER_BIRTHDATE
            birth_b = validated_birth_b
            user_data["partner_birthdate"] = birth_b
        elif not birth_b:
            await M.send_auto_delete_error(update, context, M.HINTS.MISSING_PARTNER_DATA)
            return ConversationHandler.END

        # Вычисляем профиль партнера
        try:
            profile_b = calculate_core_profile(name_b, birth_b)
            user_data["partner_profile"] = profile_b
        except Exception as e:
            await M.send_auto_delete_error(update, context, f"{M.ERRORS.CALC_PROFILE}\n{str(e)}")
            return ConversationHandler.END
            
        return ConversationHandler.END
    
    async def perform_ai_analysis(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """AI анализ для partner compatibility."""
        progress = await self.start_ai_progress(update)
        
        user_data = context.user_data
        analysis = await self.safe_ai_analysis(
            get_compatibility_interpretation,
            user_data["core_profile"],
            user_data["partner_profile"]
        )
        
        return analysis
    
    async def generate_pdf_data(self, context: ContextTypes.DEFAULT_TYPE, ai_analysis: Optional[str]) -> Dict[str, Any]:
        """Подготовка данных для генерации partner PDF."""
        user_data = context.user_data
        return {
            "name_a": user_data["name"],
            "birth_a": user_data["birthdate"],
            "profile_a": user_data["core_profile"],
            "name_b": user_data["partner_name"],
            "birth_b": user_data["partner_birthdate"],
            "profile_b": user_data["partner_profile"],
            "interpretation": ai_analysis or M.ERRORS.AI_GENERIC
        }
    
    def get_pdf_generator(self) -> Callable:
        """Возвращает функцию генерации partner PDF."""
        return generate_partner_pdf


# Экземпляр flow для использования
partner_flow = PartnerFlow()


async def request_partner_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запрос имени партнера."""
    # Очищаем предыдущие навигационные сообщения
    msg_manager = MessageManager(context)
    await msg_manager.cleanup_tracked_messages()
    
    context.user_data["selecting_partner"] = True
    await msg_manager.send_and_track(update, M.HINTS.ASK_PARTNER_NAME)
    return State.ASK_PARTNER_NAME


async def save_partner_name_and_ask_birthdate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохранение имени партнера и запрос даты рождения."""
    if not context.user_data.get("selecting_partner"):
        return

    # Очищаем промпт о вводе имени
    msg_manager = MessageManager(context)
    await msg_manager.cleanup_tracked_messages()

    context.user_data["partner_name"] = update.message.text.strip()
    await msg_manager.send_and_track(
        update,
        M.HINTS.ASK_PARTNER_BIRTHDATE
    )

    return State.ASK_PARTNER_BIRTHDATE


async def receive_partner_birthdate_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение и валидация даты рождения партнера."""
    # Очищаем промпт о вводе даты
    msg_manager = MessageManager(context)
    await msg_manager.cleanup_tracked_messages()
    
    # Use DataValidator for birthdate validation
    success, normalized = await DataValidator.validate_birthdate(
        update, context, raw_date=update.message.text.strip()
    )
    if not success:
        return State.ASK_PARTNER_BIRTHDATE
    
    context.user_data["partner_birthdate"] = normalized
    return await generate_compatibility(update, context)


async def generate_compatibility(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Генерация совместимости — использует рефакторинг базового класса."""
    return await partner_flow.execute(update, context)