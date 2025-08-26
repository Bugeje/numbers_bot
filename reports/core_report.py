import os

from jinja2 import Environment, FileSystemLoader
from weasyprint import CSS, HTML

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")


def generate_core_pdf(name: str, birthdate: str, profile: dict, analysis: str, output_path: str):
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("core_template.html")

    labels = {
        "life_path": "Жизненный путь",
        "birthday": "День рождения",
        "expression": "Выражение",
        "soul": "Душа",
        "personality": "Личность",
    }

    profile_named = {labels.get(k, k): v for k, v in profile.items()}

    html = template.render(
        name=name, birthdate=birthdate, profile=profile_named, analysis=analysis.strip()
    )

    css_path = os.path.join(TEMPLATE_DIR, "report_style.css")
    HTML(string=html).write_pdf(output_path, stylesheets=[CSS(filename=css_path)])
