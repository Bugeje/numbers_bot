import os
from datetime import datetime

from jinja2 import Environment, FileSystemLoader
from weasyprint import CSS, HTML

from calc.cycles import MONTH_NAMES, calculate_personal_year

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")


def create_months_report_pdf(name, birthdate, months_data, output_path):
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
        current_personal_year=current_personal_year_base
    )

    css_path = os.path.join(TEMPLATE_DIR, "report_style.css")
    HTML(string=html).write_pdf(output_path, stylesheets=[CSS(filename=css_path)])
