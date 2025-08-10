import os
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")

def generate_bridges_pdf(
    name: str,
    birthdate: str,
    bridges: dict,
    analysis_bridges: str,
    output_path: str
):
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("bridges_template.html")

    BRIDGE_LABELS = {
        "expression_soul": "Выражение — Душа",
        "soul_personality": "Душа — Личность",
        "life_soul": "Путь — Душа",
        "life_personality": "Путь — Личность"
    }

    bridges_named = {
        BRIDGE_LABELS.get(k, k): v for k, v in bridges.items()
    }

    html = template.render(
        name=name,
        birthdate=birthdate,
        bridges=bridges_named,
        analysis_bridges=analysis_bridges.strip()
    )

    css_path = os.path.join(TEMPLATE_DIR, "report_style.css")
    HTML(string=html).write_pdf(output_path, stylesheets=[CSS(filename=css_path)])
