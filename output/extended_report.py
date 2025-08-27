import os

from jinja2 import Environment, FileSystemLoader
from weasyprint import CSS, HTML

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")


def generate_extended_pdf(
    name: str, birthdate: str, extended: dict, analysis_ext: str, output_path: str
):
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("extended_template.html")

    labels = {
        "balance": "Равновесие",
        "growth": "Рост",
        "maturity": "Реализация",
        "rational": "Разум",
    }

    extended_named = {labels.get(k, k): v for k, v in extended.items()}

    html = template.render(
        name=name, birthdate=birthdate, extended=extended_named, analysis_ext=analysis_ext.strip()
    )

    css_path = os.path.join(TEMPLATE_DIR, "report_style.css")
    HTML(string=html).write_pdf(output_path, stylesheets=[CSS(filename=css_path)])
