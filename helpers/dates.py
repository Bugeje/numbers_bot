import re
from datetime import datetime

SUPPORTED_FORMATS = [
    "%d.%m.%Y",
    "%d/%m/%Y",
    "%Y-%m-%d",
    "%d-%m-%Y",
    "%d %m %Y",
]


def parse_and_normalize(date_str: str) -> str:
    s = (date_str or "").strip()
    if not s:
        raise ValueError("Дата пустая. Введите, например: 24.02.1993")

    # унифицируем разделители: пробелы/слэши/дефисы → точки
    s = re.sub(r"[,\u200e\u200f]", " ", s)
    s = re.sub(r"\s+", ".", s)
    s = re.sub(r"[/-]", ".", s)
    s = re.sub(r"\.+", ".", s).strip(".")

    # пробуем базовые форматы
    for fmt in SUPPORTED_FORMATS:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.strftime("%d.%m.%Y")
        except ValueError:
            pass

    # пробуем уже нормализованную строку вида DD.MM.YYYY / DD.MM.YY
    for fmt in ("%d.%m.%Y", "%d.%m.%y"):
        try:
            dt = datetime.strptime(s, fmt)
            if dt.year < 100:  # 2‑значный год: 00–29 → 2000‑е, 30–99 → 1900‑е
                year = dt.year + (2000 if dt.year <= 29 else 1900)
                dt = dt.replace(year=year)
            return dt.strftime("%d.%m.%Y")
        except ValueError:
            pass

    raise ValueError("Неверный формат даты. Примеры: 24.02.1993, 1993-02-24, 24/02/1993")


MONTHS_RU = {
    "янв": 1,
    "январь": 1,
    "фев": 2,
    "февраль": 2,
    "мар": 3,
    "март": 3,
    "апр": 4,
    "апрель": 4,
    "май": 5,
    "май": 5,
    "июн": 6,
    "июнь": 6,
    "июл": 7,
    "июль": 7,
    "авг": 8,
    "август": 8,
    "сен": 9,
    "сентябрь": 9,
    "окт": 10,
    "октябрь": 10,
    "ноя": 11,
    "ноябрь": 11,
    "дек": 12,
    "декабрь": 12,
}


def parse_year(text: str, *, lo: int = 1900, hi: int = 2100) -> int:
    s = (text or "").strip()
    if not re.fullmatch(r"\d{4}", s):
        raise ValueError("Неверный формат года. Введите 4 цифры, например: 2025.")
    year = int(s)
    if not (lo <= year <= hi):
        raise ValueError(f"Год вне диапазона {lo}–{hi}. Введите, например: 2025.")
    return year


def parse_month(text: str) -> int:
    s = (text or "").strip().lower()
    if s.isdigit():
        n = int(s)
        if 1 <= n <= 12:
            return n
        raise ValueError("Месяц вне диапазона 1–12. Пример: 8 или «август».")
    n = MONTHS_RU.get(s)
    if not n:
        raise ValueError("Месяц не распознан. Введите 1–12 или название (например, «август»).")
    return n


def parse_month_year(text: str) -> tuple[int, int]:
    """
    Принимает строки вида:
      - 08.2025, 8.2025
      - 08/2025, 8/2025
      - 2025-08, 2025/8, 2025.08
      - пробелы допускаются: '08 . 2025'
    Возвращает (month:int 1..12, year:int 1900..2100).
    """
    s = (text or "").strip()

    # Унифицируем разделители
    s = re.sub(r"\s+", "", s)
    s = s.replace(",", ".")
    s = s.replace("/", ".")
    s = s.replace("-", ".")

    # Допустимые формы: MM.YYYY или YYYY.MM
    m1 = re.fullmatch(r"(0?[1-9]|1[0-2])\.(\d{4})", s)  # MM.YYYY
    m2 = re.fullmatch(r"(\d{4})\.(0?[1-9]|1[0-2])", s)  # YYYY.MM

    if m1:
        month = int(m1.group(1))
        year = int(m1.group(2))
    elif m2:
        year = int(m2.group(1))
        month = int(m2.group(2))
    else:
        raise ValueError("Неверный формат. Введите месяц и год, например: 08.2025 или 2025-08")

    if not (1900 <= year <= 2100):
        raise ValueError("Год вне диапазона 1900–2100.")
    if not (1 <= month <= 12):
        raise ValueError("Месяц должен быть от 1 до 12.")

    return month, year
