# helpers/data_validator.py
"""
Универсальный валидатор данных для устранения дублирования.
"""
from datetime import datetime
from typing import Optional, Tuple, Dict, Any
from telegram import Update
from telegram.ext import ContextTypes

from helpers.messages import M
from helpers import normalize_name, parse_and_normalize


class DataValidator:
    """Универсальный валидатор с часто используемыми проверками."""
    
    @staticmethod
    async def validate_name(
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE, 
        key: str = "name"
    ) -> Tuple[bool, Optional[str]]:
        """
        Валидация имени.
        Возвращает (success, normalized_name).
        """
        try:
            name = normalize_name(context.user_data.get(key))
            return True, name
        except Exception as e:
            await update.effective_message.reply_text(
                f"{M.ERRORS.NAME_PREFIX}{e}\n\n{M.HINTS.ASK_NAME_FULL}"
            )
            return False, None
    
    @staticmethod
    async def validate_birthdate(
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE,
        raw_date: Optional[str] = None,
        key: str = "birthdate"
    ) -> Tuple[bool, Optional[str]]:
        """
        Валидация даты рождения.
        Возвращает (success, normalized_date).
        """
        if raw_date is None:
            raw_date = (
                update.message.text.strip() if update.message 
                else context.user_data.get(key)
            )
        
        try:
            birthdate = parse_and_normalize(raw_date)
            
            # Проверка на будущую дату
            try:
                dt = datetime.strptime(birthdate, "%d.%m.%Y")
                if dt.date() > datetime.now().date():
                    raise ValueError(M.ERRORS.DATE_FUTURE)
            except ValueError:
                pass  # Если формат другой, полагаемся на parse_and_normalize
            
            return True, birthdate
        except Exception as e:
            await update.effective_message.reply_text(
                f"{M.ERRORS.DATE_PREFIX}{e}\n\n{M.DATE_FORMATS_NOTE}\n{M.HINTS.ASK_BIRTHDATE_COMPACT}"
            )
            return False, None
    
    @staticmethod
    def validate_user_data_keys(context: ContextTypes.DEFAULT_TYPE, required_keys: list[str]) -> bool:
        """Проверка наличия обязательных ключей в user_data."""
        user_data = context.user_data
        return all(user_data.get(key) for key in required_keys)
    
    @staticmethod
    async def validate_basic_profile(
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Валидация базового профиля (name, birthdate, core_profile).
        Возвращает (success, validated_data).
        """
        required_keys = ["name", "birthdate", "core_profile"]
        
        if not DataValidator.validate_user_data_keys(context, required_keys):
            await M.send_auto_delete_error(update, context, M.HINTS.MISSING_BASIC_DATA)
            return False, None
        
        return True, {key: context.user_data[key] for key in required_keys}
    
    @staticmethod
    async def validate_partner_data(
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Валидация данных партнёра.
        Возвращает (success, partner_data).
        """
        required_keys = ["partner_name", "partner_birthdate", "partner_profile"]
        
        if not DataValidator.validate_user_data_keys(context, required_keys):
            await M.send_auto_delete_error(update, context, M.HINTS.MISSING_PARTNER_DATA)
            return False, None
        
        return True, {key: context.user_data[key] for key in required_keys}
    
    @staticmethod
    async def validate_year_data(
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> Tuple[bool, Optional[int]]:
        """
        Валидация года для анализа циклов.
        Возвращает (success, year).
        """
        year = context.user_data.get("year")
        if not year:
            await M.send_auto_delete_error(update, context, M.HINTS.MISSING_YEAR)
            return False, None
        
        try:
            return True, int(year)
        except (ValueError, TypeError):
            await M.send_auto_delete_error(update, context, M.ERRORS.DATE_PREFIX + "Некорректный год")
            return False, None


class ValidationResult:
    """Результат валидации с удобными методами."""
    
    def __init__(self, success: bool, data: Optional[Dict[str, Any]] = None, error_msg: str = ""):
        self.success = success
        self.data = data or {}
        self.error_msg = error_msg
    
    def is_valid(self) -> bool:
        return self.success
    
    def get_data(self, key: str = None) -> Any:
        if key:
            return self.data.get(key)
        return self.data
    
    @classmethod
    def success_result(cls, data: Dict[str, Any]) -> 'ValidationResult':
        return cls(True, data)
    
    @classmethod
    def error_result(cls, error_msg: str) -> 'ValidationResult':
        return cls(False, error_msg=error_msg)