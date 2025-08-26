import datetime
import os

from jinja2 import Environment, FileSystemLoader
from weasyprint import CSS, HTML

from numerology.cycles import MONTH_NAMES
from numerology.utils import extract_base

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")

LEGEND_COLORS = {
    "match-life_path": "#e74c3c",
    "match-expression": "#3498db",
    "match-soul": "#9b59b6",
    "match-personality": "#f39c12",
    "match-birthday": "#2ecc71",
}


def build_segmented_gradient(colors: list[str]) -> str:
    if len(colors) == 1:
        return f"background: {colors[0]}; color: white;"
    step = 100 / len(colors)
    segments = [
        f"{color} {round(i*step,2)}%, {color} {round((i+1)*step,2)}%"
        for i, color in enumerate(colors)
    ]
    return f"background: linear-gradient(90deg, {', '.join(segments)}); color: white;"


def mark_calendar_cells(personal_calendar, core_profile):
    highlights = {
        "match-life_path": extract_base(core_profile["life_path"]),
        "match-expression": extract_base(core_profile["expression"]),
        "match-soul": extract_base(core_profile["soul"]),
        "match-personality": extract_base(core_profile["personality"]),
        "match-birthday": extract_base(core_profile["birthday"]),
    }

    matches_by_day = {}

    for week in personal_calendar:
        for cell in week:
            if not cell:
                continue
            number = int(cell["number"])
            match_classes = [k for k, v in highlights.items() if number == v]

            if match_classes:
                matches_by_day[cell["number"]] = [k.replace("match-", "") for k in match_classes]

            if len(match_classes) == 1:
                cell["css_class"] = f"calendar-cell {match_classes[0]}"
            elif match_classes:
                colors = [LEGEND_COLORS[c] for c in match_classes]
                cell["css_class"] = "calendar-cell"
                cell["style"] = build_segmented_gradient(colors)
            else:
                cell["css_class"] = "calendar-cell"
    return personal_calendar, matches_by_day


def generate_pdf(
    name,
    birthdate,
    profile,
    filename,
    personal_calendar,
    calendar_month,
    calendar_year,
    calendar_text="",
):
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("calendar_template.html")

    calendar_month_name = MONTH_NAMES[int(calendar_month) - 1] if calendar_month else ""

    # Обработка совпадений и цветовой разметки
    personal_calendar, _ = mark_calendar_cells(personal_calendar, profile)

    # Генерация HTML с подстановкой всех переменных
    html = template.render(
        name=name,
        birthdate=birthdate,
        personal_calendar=personal_calendar,
        calendar_month=calendar_month,
        calendar_year=calendar_year,
        calendar_month_name=calendar_month_name,
        calendar_text=calendar_text,
        date=datetime.date.today().strftime("%d.%m.%Y"),
    )

    css_path = os.path.join(TEMPLATE_DIR, "report_style.css")
    HTML(string=html).write_pdf(filename, stylesheets=[CSS(filename=css_path)])
