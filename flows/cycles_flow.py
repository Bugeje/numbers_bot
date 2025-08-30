from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
import tempfile

from calc.cycles import (
    calculate_pinnacles_with_periods,
    generate_personal_year_table,
    split_years_by_pinnacles,
)
from intelligence import get_cycles_analysis
from output import generate_cycles_pdf
from helpers import PRESETS, M, FILENAMES, MessageManager, Progress, action_typing, action_upload, run_blocking
from helpers.keyboards import build_after_analysis_keyboard


async def show_cycles_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Очищаем предыдущие навигационные сообщения
        msg_manager = MessageManager(context)
        await msg_manager.cleanup_tracked_messages()
        
        name = context.user_data["name"]
        birthdate = context.user_data["birthdate"]
        life_path = context.user_data["core_profile"]["life_path"]

        # --- прогресс: расчёты ---
        await action_typing(update.effective_chat)
        progress = await Progress.start(update, M.PROGRESS.PREPARE_CYCLES)

        # Вычисления
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

        # --- прогресс: ИИ-анализ ---
        await progress.set(M.PROGRESS.AI_ANALYSIS)

        try:
            ai_analysis = await get_cycles_analysis(
                name=name,
                birthdate=birthdate,
                life_path=life_path,
                personal_years=personal_years,
                pinnacles=pinnacles,
                personal_year_blocks=personal_year_blocks
            )
            # Просто проверяем, что получили непустой результат
            if not ai_analysis or not ai_analysis.strip():
                ai_analysis = M.ERRORS.AI_GENERIC
        except Exception as e:
            # Логируем ошибку для отладки
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in cycles AI analysis: {e}")
            ai_analysis = M.ERRORS.AI_GENERIC

        # --- прогресс: PDF ---
        await progress.set(M.PROGRESS.PDF_ONE)
        await action_upload(update.effective_chat)

        # Генерация PDF
        try:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                output_path = tmp.name

            await run_blocking(
                generate_cycles_pdf, 
                name=name,
                birthdate=birthdate, 
                personal_years=personal_years_dict,  # Используем исходные данные для PDF
                pinnacles=pinnacles_dict, 
                personal_year_blocks=personal_year_blocks_list,
                ai_analysis=ai_analysis,
                output_path=output_path
            )

            await progress.set(M.PROGRESS.SENDING_ONE)
            await action_upload(update.effective_chat)

            with open(output_path, "rb") as pdf_file:
                await update.message.reply_document(
                    document=pdf_file, filename=FILENAMES.CYCLES, caption=M.DOCUMENT_READY
                )

            await progress.finish()
        except Exception:
            await progress.fail(M.ERRORS.PDF_FAIL)

        # Отправляем новое навигационное сообщение (трекаем для последующей очистки)
        msg_manager = MessageManager(context)
        await msg_manager.send_navigation_message(
            update, M.HINTS.NEXT_STEP, reply_markup=build_after_analysis_keyboard()
        )

        return ConversationHandler.END

    except Exception as e:
        await M.send_auto_delete_error(update, context, M.ERRORS.CALC_CYCLES)
        raise e
