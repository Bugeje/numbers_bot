from .bridges import calculate_bridge
from .math import extract_base


def compare_core_profiles(profile_a: dict, profile_b: dict) -> list[dict]:
    """Создаёт таблицу сопоставления двух базовых профилей."""

    components = ["life_path", "birthday", "expression", "soul", "personality"]
    labels = {
        "life_path": "Число жизненного пути",
        "birthday": "Число рождения",
        "expression": "Число выражения",
        "soul": "Число души",
        "personality": "Число личности",
    }

    table = []
    for comp in components:
        val_a = profile_a.get(comp)
        val_b = profile_b.get(comp)
        base_a = extract_base(val_a)
        base_b = extract_base(val_b)
        match = base_a == base_b
        bridge = calculate_bridge(val_a, val_b)

        table.append(
            {
                "component": comp,
                "label": labels[comp],
                "value_a": val_a,
                "value_b": val_b,
                "match": match,
                "bridge": bridge,
            }
        )
    return table


def score_compatibility(comparison_table: list[dict]) -> int:
    """Подсчитывает итоговый балл совместимости."""

    score = 0
    for row in comparison_table:
        if row["match"]:
            score += 2
        elif row["bridge"] <= 1:
            score += 1
    return score


def format_comparison_text(table: list[dict]) -> str:
    """Формирует табличный текст для визуального сравнения."""

    lines = [
        "| Компонент | Профиль A | Профиль B | Совпадение | Мост |",
        "|-----------|-----------|-----------|------------|------|",
    ]
    for row in table:
        lines.append(
            f"| {row['label']} | {row['value_a']} | {row['value_b']} | {'Да' if row['match'] else 'Нет'} | {row['bridge']} |"
        )
    return "\n".join(lines)
