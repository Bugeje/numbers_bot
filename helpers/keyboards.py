# helpers/keyboards.py
"""
Утилиты для создания клавиатур - устраняет дублирование кода создания кнопок.
"""
from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Optional, Union
from helpers.messages import BTN


class KeyboardBuilder:
    """Строитель клавиатур для устранения дублирования кода."""
    
    @staticmethod
    def create_reply_keyboard(
        buttons: List[Union[str, List[str]]], 
        resize_keyboard: bool = True,
        one_time_keyboard: bool = False,
        selective: bool = False
    ) -> ReplyKeyboardMarkup:
        """
        Создание обычной клавиатуры из списка кнопок.
        
        Args:
            buttons: Список кнопок или список списков кнопок для рядов
            resize_keyboard: Автоматически подогнать размер
            one_time_keyboard: Скрыть после использования
            selective: Показать только определённым пользователям
        """
        keyboard = []
        
        for button in buttons:
            if isinstance(button, list):
                # Ряд кнопок
                keyboard.append([KeyboardButton(text) for text in button])
            else:
                # Одна кнопка в ряду
                keyboard.append([KeyboardButton(button)])
        
        return ReplyKeyboardMarkup(
            keyboard, 
            resize_keyboard=resize_keyboard,
            one_time_keyboard=one_time_keyboard,
            selective=selective
        )
    
    @staticmethod
    def create_inline_keyboard(
        buttons: List[Union[dict, List[dict]]]
    ) -> InlineKeyboardMarkup:
        """
        Создание инлайн клавиатуры.
        
        Args:
            buttons: Список кнопок вида {"text": "Текст", "callback_data": "data"}
                    или список списков для рядов
        """
        keyboard = []
        
        for button in buttons:
            if isinstance(button, list):
                # Ряд кнопок
                row = []
                for btn in button:
                    if "url" in btn:
                        row.append(InlineKeyboardButton(btn["text"], url=btn["url"]))
                    else:
                        row.append(InlineKeyboardButton(btn["text"], callback_data=btn["callback_data"]))
                keyboard.append(row)
            else:
                # Одна кнопка в ряду
                if "url" in button:
                    keyboard.append([InlineKeyboardButton(button["text"], url=button["url"])])
                else:
                    keyboard.append([InlineKeyboardButton(button["text"], callback_data=button["callback_data"])])
        
        return InlineKeyboardMarkup(keyboard)


class StandardKeyboards:
    """Стандартные клавиатуры проекта."""
    
    @staticmethod
    def after_analysis_keyboard() -> ReplyKeyboardMarkup:
        """Клавиатура после анализа - заменяет build_after_analysis_keyboard()."""
        buttons = [
            [BTN.CORE, BTN.PARTNER],
            [BTN.EXTENDED, BTN.BRIDGES],
            [BTN.CYCLES, BTN.MONTHS],
            [BTN.CALENDAR_DAYS],
            [BTN.RESTART]
        ]
        return KeyboardBuilder.create_reply_keyboard(buttons)
    
    @staticmethod
    def main_menu_keyboard() -> ReplyKeyboardMarkup:
        """Главное меню."""
        buttons = [
            [BTN.CORE],
            [BTN.EXTENDED, BTN.BRIDGES],
            [BTN.CYCLES, BTN.PARTNER],
            [BTN.RESTART]
        ]
        return KeyboardBuilder.create_reply_keyboard(buttons)
    
    @staticmethod
    def profile_analysis_keyboard() -> ReplyKeyboardMarkup:
        """Клавиатура для выбора типа анализа профиля."""
        buttons = [
            [BTN.CORE],
            [BTN.EXTENDED, BTN.BRIDGES],
            [BTN.RESTART]
        ]
        return KeyboardBuilder.create_reply_keyboard(buttons)
    
    @staticmethod
    def cycles_analysis_keyboard() -> ReplyKeyboardMarkup:
        """Клавиатура для анализа циклов."""
        buttons = [
            ["📅 Календарь дней", "📊 Анализ месяцев"],
            [BTN.CYCLES],
            [BTN.RESTART]
        ]
        return KeyboardBuilder.create_reply_keyboard(buttons)


class KeyboardUtils:
    """Утилиты для работы с клавиатурами."""
    
    @staticmethod
    def add_restart_button(keyboard: ReplyKeyboardMarkup) -> ReplyKeyboardMarkup:
        """Добавить кнопку Restart к существующей клавиатуре."""
        new_keyboard = keyboard.keyboard.copy()
        new_keyboard.append([KeyboardButton(BTN.RESTART)])
        
        return ReplyKeyboardMarkup(
            new_keyboard,
            resize_keyboard=keyboard.resize_keyboard,
            one_time_keyboard=keyboard.one_time_keyboard,
            selective=keyboard.selective
        )
    
    @staticmethod
    def create_numbered_buttons(items: List[str], prefix: str = "") -> List[str]:
        """Создать пронумерованные кнопки из списка элементов."""
        return [f"{prefix}{i+1}. {item}" for i, item in enumerate(items)]
    
    @staticmethod
    def create_grid_keyboard(
        buttons: List[str], 
        columns: int = 2
    ) -> ReplyKeyboardMarkup:
        """Создать клавиатуру в виде сетки."""
        rows = []
        for i in range(0, len(buttons), columns):
            row = buttons[i:i+columns]
            rows.append(row)
        
        return KeyboardBuilder.create_reply_keyboard(rows)
    
    @staticmethod
    def create_yes_no_keyboard(
        yes_text: str = "✅ Да", 
        no_text: str = "❌ Нет"
    ) -> ReplyKeyboardMarkup:
        """Создать клавиатуру Да/Нет."""
        return KeyboardBuilder.create_reply_keyboard([[yes_text, no_text]])


# Алиасы для совместимости с существующим кодом
def build_after_analysis_keyboard() -> ReplyKeyboardMarkup:
    """Алиас для совместимости."""
    return StandardKeyboards.after_analysis_keyboard()


def build_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Алиас для главного меню."""
    return StandardKeyboards.main_menu_keyboard()