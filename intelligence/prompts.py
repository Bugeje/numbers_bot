def profile_prompt(profile: dict) -> str:
    return (
        f"Число жизненного пути: {profile.get('life_path', '–')}\n"
        f"Число дня рождения: {profile.get('birthday', '–')}\n"
        f"Число выражения: {profile.get('expression', '–')}\n"
        f"Число души: {profile.get('soul', '–')}\n"
        f"Число личности: {profile.get('personality', '–')}\n\n"
    )


def extended_prompt(extended: dict) -> str:
    return (
        f"📌 Равновесие: {extended.get('balance', '–')}\n"
        f"📌 Рост: {extended.get('growth', '–')}\n"
        f"📌 Реализация: {extended.get('realization', '–')}\n"
        f"📌 Разум: {extended.get('mind', '–')}\n\n"
    )


def bridges_prompt(bridges: dict) -> str:
    return (
        f"Мост Выражение—Душа: {bridges.get('expression_soul', '–')}\n"
        f"Мост Душа—Личность: {bridges.get('soul_personality', '–')}\n"
        f"Мост Путь—Душа: {bridges.get('life_soul', '–')}\n"
        f"Мост Путь—Личность: {bridges.get('life_personality', '–')}\n\n"
    )


def compatibility_prompt(profile_a: dict, profile_b: dict) -> str:
    return (
        f"Партнёр A:\n"
        f"  ЖП: {profile_a.get('life_path', '–')}  День: {profile_a.get('birthday', '–')}\n"
        f"  Выражение: {profile_a.get('expression', '–')}  Душа: {profile_a.get('soul', '–')}  Личность: {profile_a.get('personality', '–')}\n\n"
        f"Партнёр B:\n"
        f"  ЖП: {profile_b.get('life_path', '–')}  День: {profile_b.get('birthday', '–')}\n"
        f"  Выражение: {profile_b.get('expression', '–')}  Душа: {profile_b.get('soul', '–')}  Личность: {profile_b.get('personality', '–')}\n\n"
    )


def days_prompt(
    month_name: str,
    personal_month: int,
    single_components: list[str],
    gradients: list[str],
    fusion_groups: list[str],
) -> str:
    legend = {
        "match-life_path": "🟥",
        "match-expression": "🟦",
        "match-soul": "🟣",
        "match-personality": "🟨",
        "match-birthday": "🟩",
    }

    basic_colors = [legend.get(key, "") for key in single_components if key in legend]

    fusion_blocks = []
    for group in fusion_groups:
        parts = group.split("+")
        colors = [legend.get(part, "") for part in parts]
        if all(colors):
            fusion_blocks.append("".join(colors))

    text = f"Анализируемый месяц: {month_name}\n" f"Индивидуальный месяц: {personal_month}\n"

    if basic_colors:
        text += f"\nЦветовые акценты месяца: {', '.join(basic_colors)}"

    if fusion_blocks:
        text += "\n\nСлияния цветов в некоторые моменты месяца:\n"
        for fusion in fusion_blocks:
            text += f"- {fusion}\n"

    return text.strip()


from helpers.i18n import RU_MONTHS_FULL


def months_year_prompt(year: int, months_map: dict[int,int], matches_map: dict[int,list[str]]) -> str:
    """
    months_map: {1..12 -> personal_month_number}
    matches_map: {1..12 -> ["match-life_path", "match-expression", ...]}
    """
    lines = [f"Год: {year}"]
    for m in range(1, 13):
        pm = months_map.get(m, "-")
        tags = matches_map.get(m, [])
        tag_txt = ", ".join(tags) if tags else "—"
        lines.append(f"{RU_MONTHS_FULL[m]}: персональный месяц {pm}; совпадения: {tag_txt}")
    return "\n".join(lines) + "\n"
