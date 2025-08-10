MASTER_NUMBERS = {11, 22, 33, 44, 55, 66, 77, 88, 99}
KARMIC_NUMBERS = {13, 14, 16, 19}

def reduce_number(n: int) -> str:
    original = n
    while n > 9:
        n = sum(int(d) for d in str(n))
    if original in MASTER_NUMBERS or original in KARMIC_NUMBERS:
        return f"{n}({original})"
    return str(n)

def extract_base(value: str | int) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        if "(" in value:
            return int(value.split("(")[0].strip())
        return int(value.strip())
    raise ValueError(f"Некорректный формат значения: {value}")

def sum_digits_from_date_parts(date_parts: list[str]) -> int:
    return sum(int(part) for part in date_parts)
