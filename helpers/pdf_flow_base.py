# helpers/pdf_flow_base.py
"""
Базовый класс для всех PDF flow с унифицированной логикой генерации.
Устраняет дублирование кода между flows.
"""

import tempfile
import os
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Callable

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from helpers import run_blocking, M, FILENAMES
from helpers.progress import PRESETS, MessageManager, Progress, action_typing, action_upload


class BasePDFFlow(ABC):
    """
    Базовый класс для PDF flow с унифицированной логикой:
    1. Валидация данных
    2. AI анализ (опционально)
    3. Генерация PDF
    4. Отправка пользователю
    5. Навигационное сообщение
    """
    
    def __init__(self, filename: str, requires_ai: bool = True):
        self.filename = filename
        self.requires_ai = requires_ai
    
    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Основной метод выполнения flow."""
        # 1. Очистка предыдущих сообщений
        msg_manager = MessageManager(context)
        await msg_manager.cleanup_tracked_messages()
        
        # 2. Валидация данных
        validation_result = await self.validate_data(update, context)
        if validation_result != ConversationHandler.END:
            return validation_result
        
        # 3. AI анализ (если требуется)
        ai_analysis = None
        if self.requires_ai:
            ai_analysis = await self.perform_ai_analysis(update, context)
        
        # 4. Генерация и отправка PDF
        await self.generate_and_send_pdf(update, context, ai_analysis)
        
        # 5. Финальная навигация
        from interface import build_after_analysis_keyboard
        await msg_manager.send_navigation_message(
            update, M.HINTS.NEXT_STEP, reply_markup=build_after_analysis_keyboard()
        )
        
        return ConversationHandler.END
    
    @abstractmethod
    async def validate_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Валидация необходимых данных. Возвращает ConversationHandler.END если OK."""
        pass
    
    @abstractmethod
    async def perform_ai_analysis(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """Выполнение AI анализа. Возвращает результат анализа."""
        pass
    
    @abstractmethod
    async def generate_pdf_data(self, context: ContextTypes.DEFAULT_TYPE, ai_analysis: Optional[str]) -> Dict[str, Any]:
        """Подготовка данных для генерации PDF."""
        pass
    
    @abstractmethod
    def get_pdf_generator(self) -> Callable:
        """Возвращает функцию генерации PDF."""
        pass
    
    async def generate_and_send_pdf(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE,
        ai_analysis: Optional[str]
    ):
        """Унифицированная логика генерации и отправки PDF."""
        
        # Прогресс: PDF
        progress = Progress(update.effective_message)
        await progress.set(M.PROGRESS.PDF_ONE)
        await action_upload(update.effective_chat)

        try:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                output_path = tmp.name

            # Получаем данные для PDF
            pdf_data = await self.generate_pdf_data(context, ai_analysis)
            pdf_generator = self.get_pdf_generator()
            
            # Генерируем PDF
            await run_blocking(pdf_generator, **pdf_data, output_path=output_path)

            await progress.set(M.PROGRESS.SENDING_ONE)
            await action_upload(update.effective_chat)

            # Отправляем PDF
            with open(output_path, "rb") as pdf_file:
                await update.effective_message.reply_document(
                    document=pdf_file, 
                    filename=self.filename, 
                    caption=M.DOCUMENT_READY
                )

            # Удаляем временный файл
            try:
                os.unlink(output_path)
            except Exception:
                pass

            await progress.finish()
        except Exception:
            await progress.fail(M.ERRORS.PDF_FAIL)

    async def start_ai_progress(self, update: Update) -> Progress:
        """Стандартный прогресс для AI анализа."""
        await action_typing(update.effective_chat)
        progress = await Progress.start(update, PRESETS["ai"][0])
        await progress.animate(PRESETS["ai"], delay=0.6)
        return progress


class StandardDataValidationMixin:
    """Стандартная валидация для основных данных профиля."""
    
    async def validate_basic_profile_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Валидация базовых данных профиля (имя, дата, core_profile)."""
        user_data = context.user_data
        name = user_data.get("name")
        birthdate = user_data.get("birthdate")
        core_profile = user_data.get("core_profile")

        if not (name and birthdate and core_profile):
            await M.send_auto_delete_error(update, context, M.HINTS.MISSING_BASIC_DATA)
            return False
        
        return True


class AIAnalysisMixin:
    """Миксин для стандартной обработки AI анализа."""
    
    async def safe_ai_analysis(self, ai_function: Callable, *args, **kwargs) -> str:
        """Безопасное выполнение AI анализа с обработкой ошибок."""
        try:
            analysis = await ai_function(*args, **kwargs)
            if M.is_ai_error(analysis):
                return M.ERRORS.AI_GENERIC
            return analysis
        except Exception:
            return M.ERRORS.AI_GENERIC