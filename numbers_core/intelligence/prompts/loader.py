from pathlib import Path
from jinja2 import Template
import json


def load_prompt(user_tmpl_path: str, system_tmpl_path: str, profile: dict):
    u_text = Path(user_tmpl_path).read_text(encoding="utf-8")
    s_text = Path(system_tmpl_path).read_text(encoding="utf-8")
    user = Template(u_text).render(profile_json=json.dumps(profile, ensure_ascii=False, indent=2))
    system = Template(s_text).render()
    return system.strip(), user.strip()
