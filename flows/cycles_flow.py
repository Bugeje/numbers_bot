# flows/cycles_flow_refactored.py
"""
Рефакторинг cycles flow с использованием базового класса.
Устраняет дублирование кода.
"""
from typing import Dict, Any, Optional, Callable

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from calc.cycles import (
    calculate_pinnacles_with_periods,
    generate_personal_year_table,
    split_years_by_pinnacles,
)
from intelligence import get_cycles_analysis
from output import generate_cycles_pdf
from helpers import M, FILENAMES, MessageManager
from helpers.pdf_flow_base import BasePDFFlow, StandardDataValidationMixin, AIAnalysisMixin
from interface import build_after_analysis_keyboard
from .states import State


class CyclesFlow(BasePDFFlow, StandardDataValidationMixin, AIAnalysisMixin):
    """Рефакторинг cycles flow с использованием базового класса."""
    
    def __init__(self):
        super().__init__(FILENAMES.CYCLES, requires_ai=True)
    
    async def validate_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Валидация данных для cycles."""
        user_data = context.user_data
        name = user_data.get("name")
        birthdate = user_data.get("birthdate")
        core_profile = user_data.get("core_profile")
        life_path = core_profile.get("life_path") if core_profile else None

        if not (name and birthdate and life_path):
            await M.send_auto_delete_error(update, context, M.HINTS.MISSING_BASIC_DATA)
            return ConversationHandler.END
            
        # Вычисления
        try:
            personal_years_dict = generate_personal_year_table(birthdate)
            pinnacles_dict = calculate_pinnacles_with_periods(birthdate, life_path)
            personal_year_blocks_list = split_years_by_pinnacles(birthdate)
            
            # Преобразуем данные в формат, ожидаемый cycles_prompt
            # 1. personal_years: dict -> list[{'year': int, 'personal_year': str}]
            personal_years = [
                {'year': year, 'personal_year': str(personal_year)} 
                for year, personal_year in personal_years_dict.items()
            ]
            
            # 2. pinnacles: dict с ключами "Вершина N (год1–год2)" -> list[{'number': str, 'start_age': int, 'end_age': int}]
            pinnacles = []
            for key, number in pinnacles_dict.items():
                # Извлекаем года из строки вида "Вершина 1 (1990–2026)"
                try:
                    year_part = key.split('(')[1].split(')')[0]  # "1990–2026"
                    start_year, end_year = year_part.split('–')
                    
                    # Вычисляем возраст на основе года рождения
                    birth_year = int(birthdate.split('.')[2])
                    start_age = int(start_year) - birth_year
                    end_age = int(end_year) - birth_year
                    
                    pinnacles.append({
                        'number': str(number),
                        'start_age': start_age,
                        'end_age': end_age
                    })
                except (IndexError, ValueError):
                    # Если не удается распарсить, пропускаем
                    continue
                    
            # 3. personal_year_blocks: list[dict] -> dict[int, list[int]]  
            personal_year_blocks = {}
            for i, block_dict in enumerate(personal_year_blocks_list, 1):
                personal_year_blocks[i] = list(block_dict.keys())
                
            # Сохраняем все вычисленные данные
            context.user_data["personal_years"] = personal_years
            context.user_data["personal_years_dict"] = personal_years_dict
            context.user_data["pinnacles"] = pinnacles
            context.user_data["pinnacles_dict"] = pinnacles_dict
            context.user_data["personal_year_blocks"] = personal_year_blocks
            context.user_data["personal_year_blocks_list"] = personal_year_blocks_list
            
        except Exception as e:
            await M.send_auto_delete_error(update, context, f"{M.ERRORS.CALC_PROFILE}\n{str(e)}")
            return ConversationHandler.END
            
        return ConversationHandler.END
    
    async def perform_ai_analysis(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """AI анализ для cycles."""
        progress = await self.start_ai_progress(update)
        
        user_data = context.user_data
        analysis = await self.safe_ai_analysis(
            get_cycles_analysis,
            name=user_data["name"],
            birthdate=user_data["birthdate"],
            life_path=user_data["core_profile"]["life_path"],
            personal_years=user_data["personal_years"],
            pinnacles=user_data["pinnacles"],
            personal_year_blocks=user_data["personal_year_blocks"]
        )
        
        return analysis
    
    async def generate_pdf_data(self, context: ContextTypes.DEFAULT_TYPE, ai_analysis: Optional[str]) -> Dict[str, Any]:
        """Подготовка данных для генерации cycles PDF."""
        user_data = context.user_data
        return {
            "name": user_data["name"],
            "birthdate": user_data["birthdate"],
            "personal_years": user_data["personal_years"],
            "pinnacles": user_data["pinnacles_dict"],  # Use the dict version
            "personal_year_blocks": user_data["personal_year_blocks_list"],  # Use the list version
            "ai_analysis": ai_analysis or M.ERRORS.AI_GENERIC,
            "output_path": ""  # Will be set by the base class
        }
    
    def get_pdf_generator(self) -> Callable:
        """Возвращает функцию генерации cycles PDF."""
        return generate_cycles_pdf


# Экземпляр flow для использования
cycles_flow = CyclesFlow()


async def show_cycles_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Циклы — использует рефакторинг базового класса."""
    return await cycles_flow.execute(update, context)