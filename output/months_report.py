import os

from jinja2 import Environment, FileSystemLoader
from weasyprint import CSS, HTML

from calc.cycles import MONTH_NAMES

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")


def create_months_report_pdf(name, birthdate, months_data, output_path):
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("months_template.html")

    html = template.render(
        name=name, birthdate=birthdate, personal_months=months_data, month_names=MONTH_NAMES
    )

    css_path = os.path.join(TEMPLATE_DIR, "report_style.css")
    HTML(string=html).write_pdf(output_path, stylesheets=[CSS(filename=css_path)])
