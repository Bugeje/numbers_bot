# helpers/pdf_flow_base.py
"""
Базовый класс для всех PDF flow с унифицированной логикой генерации.
Устраняет дублирование кода между flows.
"""

import tempfile
import os
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Callable

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from helpers import run_blocking, M, FILENAMES, generate_pdf_async
from helpers.progress import PRESETS, MessageManager, Progress, action_typing, action_upload
from helpers.ai_analyzer import AIAnalyzer


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
        progress = None
        if self.requires_ai:
            ai_analysis, progress = await self.perform_ai_analysis_with_progress(update, context)
        
        # 4. Генерация и отправка PDF
        await self.generate_and_send_pdf(update, context, ai_analysis, progress)
        
        # 5. Финальная навигация
        # Импортируем локально чтобы избежать циклического импорта
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
    
    async def perform_ai_analysis_with_progress(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> tuple[str, Progress]:
        """Выполнение AI анализа с прогрессом. Возвращает (результат анализа, объект прогресса)."""
        # Используем AIAnalyzer для унифицированной обработки с прогрессом
        return await AIAnalyzer.analysis_with_progress(
            update, self.perform_ai_analysis, update, context
        )
    
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
        ai_analysis: Optional[str],
        ai_progress: Optional[Progress] = None
    ):
        """Унифицированная логика генерации и отправки PDF."""
        
        # Используем существующий AI прогресс или создаем новый
        progress = ai_progress
        if progress is None:
            progress = Progress(update.effective_message)
            await progress.set(M.PROGRESS.AI_LABEL)  # Using AI_LABEL as a generic progress message
        
        await action_upload(update.effective_chat)

        try:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                output_path = tmp.name

            # Получаем данные для PDF
            pdf_data = await self.generate_pdf_data(context, ai_analysis)
            pdf_generator = self.get_pdf_generator()
            
            # Handle different parameter names for output path
            if "output_path" in pdf_data:
                pdf_data["output_path"] = output_path
            elif "filename" in pdf_data:
                pdf_data["filename"] = output_path
            else:
                # Add output_path to the data for functions that expect it
                pdf_data["output_path"] = output_path

            # Генерируем PDF через очередь
            result_path = await generate_pdf_async(pdf_generator, priority=5, timeout=120.0, **pdf_data)

            # Отправляем PDF без сообщения об успешной генерации
            with open(output_path, "rb") as pdf_file:
                await update.effective_message.reply_document(
                    document=pdf_file, 
                    filename=self.filename
                )

            # Удаляем временный файл
            try:
                os.unlink(output_path)
            except Exception:
                pass

            # Завершаем прогресс (удаляем сообщение без показа "отчет готов")
            await progress.cleanup()
        except Exception as e:
            await progress.fail(M.PROGRESS.FAIL)
            # Log the error for debugging
            logger = logging.getLogger(__name__)
            logger.error(f"PDF generation failed: {e}", exc_info=True)

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
        # Используем новый AIAnalyzer для унифицированной обработки
        return await AIAnalyzer.safe_analysis(ai_function, *args, **kwargs)
    
    async def safe_ai_analysis_with_progress(
        self, 
        update: Update, 
        ai_function: Callable, 
        *args, 
        progress_presets: list = None,
        **kwargs
    ) -> tuple[str, Progress]:
        """Безопасное выполнение AI анализа с прогрессом."""
        # Используем новый AIAnalyzer для унифицированной обработки с прогрессом
        return await AIAnalyzer.analysis_with_progress(
            update, ai_function, *args, 
            progress_presets=progress_presets, **kwargs
        )