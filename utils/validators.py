# utils/validators.py
import re


def normalize_name(raw: str) -> str:
    """
    Нормализует и валидирует ФИО:
    - разрешена ТОЛЬКО кириллица (включая расширенный диапазон), пробел и дефис
    - запятые считаем разделителями (заменяем на пробел)
    - разные виды дефисов (–, —) приводим к '-'
    - схлопываем множественные пробелы
    - Title-Case по словам и частям через дефис
    """
    s = (raw or "").strip()
    if not s:
        raise ValueError("Имя пустое. Введите, например: Анна")

    # унификация разделителей/пробелов/дефисов
    s = s.replace("\u00a0", " ")  # NBSP -> пробел
    s = s.replace(",", " ")  # запятые -> пробел
    s = s.replace("–", "-").replace("—", "-")  # длинные дефисы -> '-'
    s = re.sub(r"\s+", " ", s)  # схлопнуть пробелы

    if len(s) < 2 or len(s) > 80:
        raise ValueError("Длина имени должна быть от 2 до 80 символов.")

    # Кириллица: базовый и дополнительный блоки Unicode U+0400–U+04FF
    NAME_TOKEN = "[\u0400-\u04ff]+(?:-[\u0400-\u04ff]+)*"
    pattern = re.compile(f"^(?:{NAME_TOKEN})(?:\\s+{NAME_TOKEN}){{0,10}}$")

    if not pattern.fullmatch(s):
        raise ValueError("Имя должно содержать только кириллицу, пробел и дефис.")

    # Title-Case по словам с сохранением дефиса
    def cap_token(tok: str) -> str:
        parts = tok.split("-")
        parts = [p[:1].upper() + p[1:].lower() if p else p for p in parts]
        return "-".join(parts)

    return " ".join(cap_token(t) for t in s.split(" "))
