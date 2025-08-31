import os
import logging

from jinja2 import Environment, FileSystemLoader
from weasyprint import CSS, HTML

from calc.extended.compatibility import compare_core_profiles, score_compatibility

# Set up logging
logger = logging.getLogger(__name__)

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
    logger.info("Starting partner PDF generation")
    logger.info(f"name_a: {name_a}, birthdate_a: {birthdate_a}")
    logger.info(f"name_b: {name_b}, birthdate_b: {birthdate_b}")
    logger.info(f"profile_a keys: {list(profile_a.keys())}")
    logger.info(f"profile_b keys: {list(profile_b.keys())}")
    logger.info(f"interpretation length: {len(interpretation) if interpretation else 0}")
    logger.info(f"output_path: {output_path}")

    try:
        env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        template = env.get_template("partner_template.html")
        logger.info("Template loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load template: {e}", exc_info=True)
        raise

    try:
        comparison_table = compare_core_profiles(profile_a, profile_b)
        score = score_compatibility(comparison_table)
        logger.info(f"Comparison table generated with {len(comparison_table)} rows, score: {score}")
    except Exception as e:
        logger.error(f"Failed to generate comparison table: {e}", exc_info=True)
        raise

    labels = {
        "life_path": "Жизненный путь",
        "birthday": "День рождения",
        "expression": "Выражение",
        "soul": "Душа",
        "personality": "Личность",
    }

    try:
        profile_a_named = {labels[k]: v for k, v in profile_a.items() if k in labels}
        profile_b_named = {labels[k]: v for k, v in profile_b.items() if k in labels}
        logger.info("Profile labels converted")
    except Exception as e:
        logger.error(f"Failed to convert profile labels: {e}", exc_info=True)
        raise

    try:
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
        logger.info("HTML rendered successfully")
    except Exception as e:
        logger.error(f"Failed to render HTML: {e}", exc_info=True)
        raise

    try:
        css_path = os.path.join(TEMPLATE_DIR, "report_style.css")
        logger.info(f"Generating PDF at {output_path}")
        HTML(string=html).write_pdf(output_path, stylesheets=[CSS(filename=css_path)])
        logger.info("PDF generated successfully")
    except Exception as e:
        logger.error(f"Failed to generate PDF: {e}", exc_info=True)
        raise