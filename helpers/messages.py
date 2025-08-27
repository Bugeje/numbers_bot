# utils/messages.py


class BTN:
    CORE = "📄 Ядро личности"
    EXTENDED = "🧩 Расширенные числа"
    BRIDGES = "🪄 Мосты"
    CYCLES = "🌀 Циклы и годы"
    MONTHS = "📆 Анализ месяцев"
    CALENDAR_DAYS = "📅 Календарь дней"
    PARTNER = "💞 Совместимость партнёров"
    RESTART = "🔁 Старт"


class M:
    # ===== Прогресс / статусы =====
    class PROGRESS:
        CALC_LABEL = "⚙️ Считаю ядро личности…"
        AI_LABEL = "🤖 Генерирую интерпретацию ИИ…"
        PDF_ONE = "📝 Формирую PDF-отчёт…"
        SENDING_ONE = "📤 Отправляю отчёт…"
        DONE = "✅ Отчёт готов!"
        FAIL = "⚠️ Произошла ошибка."

    # ===== Подсказки/реплики =====
    class HINTS:
        GREETING = "Привет! Я помогу рассчитать твоё ядро личности по нумерологии."
        CALC_CORE_FIRST = "Сначала рассчитаем ядро личности."
        ASK_NAME = "Как тебя зовут (Фамилия Имя Отчество)?"
        ASK_BIRTHDATE = "📅 Введите дату рождения в формате ДД.ММ.ГГГГ (например 24.02.1993). Можно также 1993-02-24 или 24/02/1993."
        REENTER_NAME = "Введите имя ещё раз:"
        REENTER_DATE = "Введите дату ещё раз:"
        NEXT_STEP = "Выберите следующий шаг:"

    # ===== Подсказка по форматам дат =====
    DATE_FORMATS_NOTE = (
        "Примеры допустимых форматов: 24.02.1993, 24/02/1993, 1993-02-24, 24-02-1993."
    )

    # ===== Ошибки (единый стиль) =====
    class ERRORS:
        NAME_PREFIX = "❌ Проблема с именем: "
        NAME_RULES = "Имя должно содержать только кириллицу, пробел и дефис."
        DATE_PREFIX = "❌ Некорректная дата: "
        DATE_FUTURE = "Дата рождения не может быть в будущем."
        CALC_PROFILE = "❌ Ошибка при расчёте профиля."
        CALC_EXTENDED = "❌ Ошибка при расчёте расширенных чисел."
        PDF_FAIL = "⚠️ Не удалось сформировать PDF."
        AI_GENERIC = "Анализ временно недоступен. Вы можете повторить запрос позже."

    # ===== Подписи к документам =====
    class CAPTION:
        CORE = "📄 Ваш отчёт о ядре личности"
        EXTENDED = "📘 Ваш отчёт по расширенным числам"
        BRIDGES = "🪄 Отчёт по мостам"
        CYCLES = "🌀 Отчёт по циклам и годам"
        MONTHS = "📆 Отчёт по анализу месяцев"
        MONTHS_YEAR = "📅 Годовой обзор месячного календаря"
        PARTNER = "💞 Отчёт по совместимости"

    # ===== Форматтеры для кратких превью =====
    @staticmethod
    def format_core_summary(name: str, birthdate: str, profile: dict) -> str:
        title_map = {
            "life_path": "🔢 Жизненный путь",
            "birthday": "📅 День рождения",
            "expression": "🧬 Выражение",
            "soul": "💖 Душа",
            "personality": "🎭 Личность",
        }
        lines = [f"🔹 *Ядро личности для {name}*", f"📆 Дата рождения: {birthdate}", ""]
        for k, label in title_map.items():
            if k in profile:
                lines.append(f"{label}: {profile[k]}")
        return "\n".join(lines)

    @staticmethod
    def format_extended_summary(name: str, birthdate: str, extended: dict) -> str:
        labels = {
            "balance": "⚖️ Баланс",
            "growth": "🌱 Рост",
            "realization": "🎯 Реализация",
            "mind": "🧠 Разум",
        }
        lines = [f"🧩 *Расширенные числа для {name}*", f"📆 Дата рождения: {birthdate}", ""]
        for k, label in labels.items():
            if k in extended:
                lines.append(f"{label}: {extended[k]}")
        return "\n".join(lines)
