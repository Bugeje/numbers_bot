# flows/partner_flow_refactored.py
"""
Рефакторинг partner flow с использованием базового класса.
Устраняет дублирование кода.
"""
from typing import Dict, Any, Optional, Callable
import logging

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

# Set up logging
logger = logging.getLogger(__name__)

class PartnerFlow(BasePDFFlow, StandardDataValidationMixin, AIAnalysisMixin):
    """Рефакторинг partner flow с использованием базового класса."""
    
    def __init__(self):
        super().__init__(FILENAMES.PARTNER_COMPATIBILITY, requires_ai=True)
    
    async def validate_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Валидация данных для partner compatibility."""
        logger.info("Starting partner compatibility validation")
        user_data = context.user_data
        name_a = user_data.get("name")
        birth_a = user_data.get("birthdate")
        profile_a = user_data.get("core_profile")

        name_b = user_data.get("partner_name")
        birth_b = user_data.get("partner_birthdate")

        logger.info(f"User data - name_a: {name_a}, birth_a: {birth_a}, profile_a: {profile_a}")
        logger.info(f"Partner data - name_b: {name_b}, birth_b: {birth_b}")

        # Проверяем основные данные пользователя
        if not (name_a and birth_a and profile_a):
            logger.warning("Missing user basic data")
            await M.send_auto_delete_error(update, context, M.HINTS.MISSING_BASIC_DATA)
            return ConversationHandler.END

        # Проверяем данные партнера - если их нет, это нормально на этом этапе
        if not name_b:
            logger.info("Partner name not yet provided, this is expected in early stages")
            # Don't return error, let the flow continue
            return ConversationHandler.END

        # Если дата рождения партнера еще не введена, но у нас есть сообщение с ней
        if not birth_b and update.message:
            logger.info("Validating partner birthdate from message")
            success, validated_birth_b = await DataValidator.validate_birthdate(
                update, context, raw_date=update.message.text.strip()
            )
            if not success:
                logger.warning("Partner birthdate validation failed")
                return State.ASK_PARTNER_BIRTHDATE
            birth_b = validated_birth_b
            user_data["partner_birthdate"] = birth_b
        elif not birth_b:
            # Если дата рождения партнера не введена и нет сообщения с ней
            logger.info("Partner birthdate not yet provided, this is expected in early stages")
            # Don't return error, let the flow continue
            return ConversationHandler.END

        # Вычисляем профиль партнера только если у нас есть все необходимые данные
        if name_b and birth_b:
            try:
                logger.info("Calculating partner profile")
                profile_b = calculate_core_profile(name_b, birth_b)
                user_data["partner_profile"] = profile_b
                logger.info(f"Partner profile calculated: {profile_b}")
            except Exception as e:
                logger.error(f"Error calculating partner profile: {e}", exc_info=True)
                await M.send_auto_delete_error(update, context, f"{M.ERRORS.CALC_PROFILE}\n{str(e)}")
                return ConversationHandler.END
            
        # Return END to indicate validation passed and flow can continue
        return ConversationHandler.END
    
    async def perform_ai_analysis(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """AI анализ для partner compatibility."""
        logger.info("Starting AI analysis for partner compatibility")
        progress = await self.start_ai_progress(update)
        
        user_data = context.user_data
        analysis = await self.safe_ai_analysis(
            get_compatibility_interpretation,
            user_data["core_profile"],
            user_data["partner_profile"]
        )
        logger.info("AI analysis completed")
        
        return analysis
    
    async def generate_pdf_data(self, context: ContextTypes.DEFAULT_TYPE, ai_analysis: Optional[str]) -> Dict[str, Any]:
        """Подготовка данных для генерации partner PDF."""
        logger.info("Preparing PDF data")
        user_data = context.user_data
        pdf_data = {
            "name_a": user_data["name"],
            "birthdate_a": user_data["birthdate"],
            "profile_a": user_data["core_profile"],
            "name_b": user_data["partner_name"],
            "birthdate_b": user_data["partner_birthdate"],
            "profile_b": user_data["partner_profile"],
            "interpretation": ai_analysis or M.ERRORS.AI_GENERIC,
            "output_path": ""  # Will be set by the base class
        }
        logger.info("PDF data prepared")
        return pdf_data
    
    def get_pdf_generator(self) -> Callable:
        """Возвращает функцию генерации partner PDF."""
        return generate_partner_pdf
    
    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Основной метод выполнения flow."""
        logger.info(f"Starting PDF flow execution for {self.filename}")
        # 1. Очистка предыдущих сообщений
        msg_manager = MessageManager(context)
        await msg_manager.cleanup_tracked_messages()
        
        # 2. Валидация данных
        logger.info("Validating data")
        validation_result = await self.validate_data(update, context)
        if validation_result != ConversationHandler.END:
            logger.info(f"Validation failed, returning state: {validation_result}")
            return validation_result
        
        # 3. AI анализ (если требуется)
        ai_analysis = None
        progress = None
        if self.requires_ai:
            logger.info("Performing AI analysis with progress")
            ai_analysis, progress = await self.perform_ai_analysis_with_progress(update, context)
            logger.info("AI analysis completed")
        
        # 4. Генерация и отправка PDF
        logger.info("Generating and sending PDF")
        try:
            await self.generate_and_send_pdf(update, context, ai_analysis, progress)
            logger.info("PDF generation and sending completed")
        except Exception as e:
            logger.error(f"PDF generation and sending failed: {e}", exc_info=True)
            # Return to EXTENDED_ANALYSIS state even if PDF generation fails
            return State.EXTENDED_ANALYSIS
        
        # 5. Финальная навигация
        # Импортируем локально чтобы избежать циклического импорта
        from interface import build_after_analysis_keyboard
        await msg_manager.send_navigation_message(
            update, M.HINTS.NEXT_STEP, reply_markup=build_after_analysis_keyboard()
        )
        logger.info("Navigation message sent")
        
        return State.EXTENDED_ANALYSIS


# Экземпляр flow для использования
partner_flow = PartnerFlow()


async def request_partner_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запрос имени партнера."""
    logger.info("Requesting partner name")
    # Очищаем предыдущие навигационные сообщения
    msg_manager = MessageManager(context)
    await msg_manager.cleanup_tracked_messages()
    
    context.user_data["selecting_partner"] = True
    # Clear any previous partner data
    context.user_data.pop("partner_name", None)
    context.user_data.pop("partner_birthdate", None)
    context.user_data.pop("partner_profile", None)
    
    await msg_manager.send_and_track(update, M.HINTS.ASK_PARTNER_NAME)
    logger.info("Sent partner name request, returning ASK_PARTNER_NAME state")
    return State.ASK_PARTNER_NAME


async def save_partner_name_and_ask_birthdate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохранение имени партнера и запрос даты рождения."""
    logger.info("Saving partner name and asking for birthdate")
    # Очищаем промпт о вводе имени
    msg_manager = MessageManager(context)
    await msg_manager.cleanup_tracked_messages()

    context.user_data["partner_name"] = update.message.text.strip()
    logger.info(f"Partner name saved: {context.user_data['partner_name']}")
    
    await msg_manager.send_and_track(
        update,
        M.HINTS.ASK_PARTNER_BIRTHDATE
    )

    # Return the correct state to continue the conversation flow
    logger.info("Returning ASK_PARTNER_BIRTHDATE state")
    return State.ASK_PARTNER_BIRTHDATE


async def receive_partner_birthdate_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение и валидация даты рождения партнера."""
    logger.info("Receiving partner birthdate")
    # Очищаем промпт о вводе даты
    msg_manager = MessageManager(context)
    await msg_manager.cleanup_tracked_messages()
    
    # Use DataValidator for birthdate validation
    success, normalized = await DataValidator.validate_birthdate(
        update, context, raw_date=update.message.text.strip()
    )
    if not success:
        logger.warning("Partner birthdate validation failed")
        return State.ASK_PARTNER_BIRTHDATE
    
    context.user_data["partner_birthdate"] = normalized
    logger.info(f"Partner birthdate saved: {context.user_data['partner_birthdate']}")
    
    # Clear the selecting_partner flag
    context.user_data.pop("selecting_partner", None)
    
    # Generate compatibility directly
    logger.info("Generating partner compatibility")
    try:
        await partner_flow.execute(update, context)
        logger.info("Partner compatibility generation completed")
    except Exception as e:
        logger.error(f"Partner compatibility generation failed: {e}", exc_info=True)
        # Even if generation fails, we still want to return to EXTENDED_ANALYSIS state
        pass
    
    # After generating compatibility, show the navigation menu again and return to EXTENDED_ANALYSIS state
    msg_manager = MessageManager(context)
    await msg_manager.send_navigation_message(
        update, M.HINTS.NEXT_STEP, reply_markup=build_after_analysis_keyboard()
    )
    
    return State.EXTENDED_ANALYSIS


async def generate_compatibility(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Генерация совместимости — использует рефакторинг базового класса."""
    logger.info("Generating compatibility (direct call)")
    # Clear the selecting_partner flag
    context.user_data.pop("selecting_partner", None)
    try:
        await partner_flow.execute(update, context)
    except Exception as e:
        logger.error(f"Partner compatibility generation failed: {e}", exc_info=True)
        # Even if generation fails, we still want to return to EXTENDED_ANALYSIS state
    
    # After generating compatibility, show the navigation menu again and return to EXTENDED_ANALYSIS state
    msg_manager = MessageManager(context)
    await msg_manager.send_navigation_message(
        update, M.HINTS.NEXT_STEP, reply_markup=build_after_analysis_keyboard()
    )
    
    return State.EXTENDED_ANALYSIS