import os
import tempfile

from jinja2 import Environment, FileSystemLoader
from weasyprint import CSS, HTML

from calc.cycles import calculate_personal_year

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")


def format_pinnacle_numbers(pinnacles):
    return [str(value) for _, value in sorted(pinnacles.items())]


def build_pinnacle_columns(pinnacles, personal_year_blocks, birthdate):
    max_len = max(len(block) for block in personal_year_blocks)
    pinnacle_columns = []

    for header_value, block in zip(pinnacles.values(), personal_year_blocks, strict=False):
        rows = sorted(block.items())
        padded = [
            (str(year), str(calculate_personal_year(birthdate, int(year)))) for year, _ in rows
        ]
        padded += [("", "")] * (max_len - len(rows))
        pinnacle_columns.append({"header": str(header_value), "rows": padded})

    return pinnacle_columns


def generate_cycles_pdf(name, birthdate, personal_years, pinnacles, personal_year_blocks):
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    template = env.get_template("cycles_template.html")

    pinnacle_numbers = format_pinnacle_numbers(pinnacles)
    pinnacle_columns = build_pinnacle_columns(pinnacles, personal_year_blocks, birthdate)

    html_content = template.render(
        name=name,
        birthdate=birthdate,
        pinnacle_numbers=pinnacle_numbers,
        pinnacle_columns=pinnacle_columns,
    )

    css_path = os.path.join(TEMPLATES_DIR, "report_style.css")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
        HTML(string=html_content).write_pdf(tmpfile.name, stylesheets=[CSS(filename=css_path)])
        return tmpfile.name
