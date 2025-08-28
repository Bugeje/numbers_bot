import os
from datetime import datetime

from jinja2 import Environment, FileSystemLoader
from weasyprint import CSS, HTML

from calc.cycles import MONTH_NAMES, calculate_personal_year
from helpers.i18n import RU_MONTHS_FULL

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")


def create_months_report_pdf(name, birthdate, months_data, output_path, ai_text: str | None = None):
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("months_template.html")
    
    # Get current month index (0-11 for template)
    current_month_index = datetime.now().month - 1
    
    # Calculate user's current personal year
    current_personal_year = calculate_personal_year(birthdate)
    # Extract base number (remove parentheses like "5(14)" -> "5")
    current_personal_year_base = current_personal_year.split('(')[0]

    html = template.render(
        name=name, 
        birthdate=birthdate, 
        personal_months=months_data, 
        month_names=MONTH_NAMES,
        current_month_index=current_month_index,
        current_personal_year=current_personal_year_base,
        ai_text=ai_text or "",   # важно
    )

    css_path = os.path.join(TEMPLATE_DIR, "report_style.css")
    HTML(string=html).write_pdf(output_path, stylesheets=[CSS(filename=css_path)])


def create_months_year_report_pdf(
    name: str, 
    birthdate: str, 
    target_year: int,
    personal_year: int,
    months_data: list, 
    core_profile: dict,
    ai_analysis: str,
    output_path: str
):
    """Создать PDF отчет с годовым AI анализом месячного календаря."""
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("months_year_template.html")
    
    # Преобразуем данные для шаблона
    from calc.math import extract_base
    
    core_values = {
        "life_path": extract_base(core_profile.get("life_path", "0")),
        "expression": extract_base(core_profile.get("expression", "0")),
        "soul": extract_base(core_profile.get("soul", "0")),
        "personality": extract_base(core_profile.get("personality", "0")),
        "birthday": extract_base(core_profile.get("birthday", "0")),
    }
    
    # Полные названия месяцев (используем импортированные)
    month_names_full = RU_MONTHS_FULL[1:]  # Исключаем None с индекса 0
    
    # Создаем структуру данных для шаблона
    months_with_matches = []
    for i, month_value in enumerate(months_data):
        # Извлекаем базовое число из строки вида '2(11)' или '2'
        month_num = int(extract_base(month_value))
        
        # Находим совпадения
        matches = []
        for comp_name, comp_value in core_values.items():
            if month_num == comp_value:
                match_labels = {
                    "life_path": "Жизненный путь",
                    "expression": "Выражение", 
                    "soul": "Душа",
                    "personality": "Личность",
                    "birthday": "День рождения"
                }
                matches.append(match_labels[comp_name])
        
        months_with_matches.append({
            "name": month_names_full[i],
            "value": month_num,
            "matches": matches,
            "has_matches": len(matches) > 0
        })
    
    html = template.render(
        name=name,
        birthdate=birthdate,
        target_year=target_year,
        personal_year=personal_year,
        months=months_with_matches,
        core_profile=core_profile,
        ai_analysis=ai_analysis.strip() if ai_analysis else "Ошибка: AI анализ пустой",
    )
    
    css_path = os.path.join(TEMPLATE_DIR, "report_style.css")
    HTML(string=html).write_pdf(output_path, stylesheets=[CSS(filename=css_path)])
