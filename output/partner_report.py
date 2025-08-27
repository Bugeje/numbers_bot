import os

from jinja2 import Environment, FileSystemLoader
from weasyprint import CSS, HTML

from calc.extended.compatibility import compare_core_profiles, score_compatibility

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")


def generate_partner_pdf(
    name_a: str,
    birthdate_a: str,
    profile_a: dict,
    name_b: str,
    birthdate_b: str,
    profile_b: dict,
    interpretation: str,
    output_path: str,
):
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("partner_template.html")

    comparison_table = compare_core_profiles(profile_a, profile_b)
    score = score_compatibility(comparison_table)

    labels = {
        "life_path": "Жизненный путь",
        "birthday": "День рождения",
        "expression": "Выражение",
        "soul": "Душа",
        "personality": "Личность",
    }

    profile_a_named = {labels[k]: v for k, v in profile_a.items() if k in labels}
    profile_b_named = {labels[k]: v for k, v in profile_b.items() if k in labels}

    html = template.render(
        name_a=name_a,
        birthdate_a=birthdate_a,
        profile_a=profile_a_named,
        name_b=name_b,
        birthdate_b=birthdate_b,
        profile_b=profile_b_named,
        comparison_table=comparison_table,
        score=score,
        interpretation=interpretation.strip(),
    )

    css_path = os.path.join(TEMPLATE_DIR, "report_style.css")
    HTML(string=html).write_pdf(output_path, stylesheets=[CSS(filename=css_path)])
