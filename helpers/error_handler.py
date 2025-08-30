# helpers/error_handler.py
"""
Унифицированный обработчик ошибок для устранения дублирования кода обработки ошибок.
"""
import logging
from typing import Optional, Union, Any
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from helpers.messages import M


logger = logging.getLogger(__name__)


class ErrorHandler:
    """Унифицированный обработчик ошибок с различными стратегиями."""
    
    @staticmethod
    async def handle_calculation_error(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        error: Exception,
        operation_type: str = "расчёта",
        return_state: int = ConversationHandler.END
    ) -> int:
        """
        Обработка ошибок расчётов.
        
        Args:
            error: Исключение
            operation_type: Тип операции для сообщения
            return_state: Состояние для возврата
        """
        logger.error(f"Calculation error in {operation_type}: {error}")
        
        error_msg = f"❌ Ошибка при {operation_type}: {str(error)}"
        await M.send_auto_delete_error(update, context, error_msg)
        
        return return_state
    
    @staticmethod
    async def handle_validation_error(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        field_name: str,
        error_message: str,
        return_state: int
    ) -> int:
        """Обработка ошибок валидации."""
        error_msg = f"{M.ERRORS.PREFIX}{field_name}: {error_message}"
        await M.send_auto_delete_error(update, context, error_msg)
        return return_state
    
    @staticmethod
    async def handle_pdf_generation_error(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        error: Exception,
        progress_obj: Optional[Any] = None
    ):
        """Обработка ошибок генерации PDF."""
        logger.error(f"PDF generation error: {error}")
        
        if progress_obj:
            await progress_obj.fail(M.ERRORS.PDF_FAIL)
        else:
            await M.send_auto_delete_error(update, context, M.ERRORS.PDF_FAIL)
    
    @staticmethod
    async def handle_ai_analysis_error(
        error: Exception,
        fallback_message: str = None
    ) -> str:
        """
        Обработка ошибок AI анализа.
        Возвращает fallback сообщение.
        """
        logger.error(f"AI analysis error: {error}")
        return fallback_message or M.ERRORS.AI_GENERIC
    
    @staticmethod
    async def handle_generic_error(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        error: Exception,
        operation: str = "операции",
        return_state: int = ConversationHandler.END
    ) -> int:
        """Обработка общих ошибок."""
        logger.error(f"Generic error in {operation}: {error}")
        
        error_msg = M.format_error(f"Произошла ошибка при {operation}")
        await M.send_auto_delete_error(update, context, error_msg)
        
        return return_state
    
    @staticmethod
    def safe_execute(
        func,
        *args,
        error_handler: Optional[callable] = None,
        default_return: Any = None,
        **kwargs
    ):
        """
        Безопасное выполнение функции с обработкой ошибок.
        
        Args:
            func: Функция для выполнения
            error_handler: Обработчик ошибок (получает exception)
            default_return: Значение по умолчанию при ошибке
            *args, **kwargs: Аргументы для функции
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Safe execution error in {func.__name__}: {e}")
            
            if error_handler:
                error_handler(e)
            
            return default_return


class FlowErrorHandler:
    """Специализированный обработчик ошибок для flow."""
    
    @staticmethod
    async def wrap_flow_execution(
        flow_func,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        error_fallback_state: int = ConversationHandler.END
    ) -> int:
        """
        Обёртка для безопасного выполнения flow с обработкой ошибок.
        """
        try:
            return await flow_func(update, context)
        except Exception as e:
            logger.error(f"Flow execution error in {flow_func.__name__}: {e}")
            await ErrorHandler.handle_generic_error(
                update, context, e, flow_func.__name__, error_fallback_state
            )
            return error_fallback_state


class ErrorContext:
    """Контекст для накопления ошибок и их отложенной обработки."""
    
    def __init__(self):
        self.errors = []
    
    def add_error(self, error: Union[str, Exception], context: str = ""):
        """Добавить ошибку в контекст."""
        error_info = {
            "error": str(error),
            "context": context,
            "type": type(error).__name__ if isinstance(error, Exception) else "Message"
        }
        self.errors.append(error_info)
    
    def has_errors(self) -> bool:
        """Проверка наличия ошибок."""
        return len(self.errors) > 0
    
    def get_summary(self) -> str:
        """Получить сводку по ошибкам."""
        if not self.errors:
            return "Ошибок нет"
        
        summary = f"Обнаружено ошибок: {len(self.errors)}\n"
        for i, error_info in enumerate(self.errors, 1):
            context = f" [{error_info['context']}]" if error_info['context'] else ""
            summary += f"{i}. {error_info['error']}{context}\n"
        
        return summary
    
    async def send_summary_if_errors(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ):
        """Отправить сводку ошибок, если они есть."""
        if self.has_errors():
            await M.send_auto_delete_error(update, context, self.get_summary())
    
    def clear(self):
        """Очистить ошибки."""
        self.errors.clear()