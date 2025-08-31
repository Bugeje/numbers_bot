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


class FILENAMES:
    """Централизованные названия PDF файлов."""
    CORE_PROFILE = "Ядро_личности.pdf"
    EXTENDED_PROFILE = "Расширенные_числа.pdf"
    BRIDGES = "Анализ_мостов.pdf"
    CYCLES = "Циклы_и_годы.pdf"
    MONTHS = "Анализ_месяцев.pdf"
    CALENDAR_DAYS = "Календарь_дней.pdf"
    PARTNER_COMPATIBILITY = "Совместимость_партнёров.pdf"


class M:
    # ===== Прогресс / статусы =====
    class PROGRESS:
        CALC_LABEL = "⚙️ Считаю ядро личности…"
        AI_LABEL = "🤖 Генерирую интерпретацию…"
        FAIL = "⚠️ Произошла ошибка."

    # ===== Подсказки/реплики =====
    class HINTS:
        ASK_NAME_FULL = "Привет! Я помогу рассчитать твоё ядро личности по нумерологии.\n\nКак тебя зовут (Фамилия, Имя, Отчество)?"
        ASK_BIRTHDATE_COMPACT = "📅 Введите дату рождения в формате ДД.ММ.ГГГГ (например 24.02.1993).Можно также 1993-02-24 или 24/02/1993."
        ASK_PARTNER_NAME = "Введите имя и фамилию второго партнёра:"
        ASK_PARTNER_BIRTHDATE = "📅 Введите дату рождения партнёра в формате ДД.ММ.ГГГГ (например 24.02.1993)."
        NEXT_STEP = "Выберите следующий шаг:"
        MISSING_BASIC_DATA = "⚠️ Сначала введите имя и дату рождения."
        MISSING_YEAR = "⚠️ Не хватает года для анализа. Пожалуйста, начните заново."
        MISSING_PARTNER_DATA = "❌ Не удалось получить дату рождения партнёра."

    # ===== Подсказка по форматам дат =====
    DATE_FORMATS_NOTE = (
        "Примеры допустимых форматов: 24.02.1993, 24/02/1993, 1993-02-24, 24-02-1993."
    )

    # ===== Ошибки (единый стиль) =====
    class ERRORS:
        # Общие ошибки
        PREFIX = "❌ Ошибка: "
        GENERIC_ERROR = "❌ Произошла ошибка при обработке запроса."
        
        # Ошибки имен и дат
        NAME_PREFIX = "❌ Проблема с именем: "
        NAME_RULES = "Имя должно содержать только кириллицу, пробел и дефис."
        DATE_PREFIX = "❌ Некорректная дата: "
        DATE_FUTURE = "Дата рождения не может быть в будущем."
        
        # Ошибки расчетов
        CALC_PROFILE = "❌ Ошибка при расчёте профиля."
        
        # Ошибки PDF и файлов
        PDF_FAIL = "⚠️ Не удалось сформировать PDF."
        
        # Ошибки AI
        AI_GENERIC = "Анализ временно недоступен. Вы можете повторить запрос позже."
        AI_NO_KEY = "❌ Ошибка: отсутствует API-ключ OpenRouter. Проверь .env."
        AI_EMPTY = "Ошибка: AI анализ недоступен"
        AI_UNEXPECTED = "❌ Неожиданный ответ от API"
        
        # Ошибки сети и конфигурации
        NETWORK_ERROR = "❌ Сетевая ошибка"
        API_ERROR = "❌ Ошибка API"

    # ===== Описания цветных меток календаря =====
    class CALENDAR_LEGENDS:
        LIFE_PATH = "🟥 Жизненный путь — тема предназначения, судьбоносные акценты"
        EXPRESSION = "🟦 Выражение — энергия действия, реализация потенциала"
        SOUL = "🟣 Душа — внутренние желания и эмоциональные импульсы"
        PERSONALITY = "🟨 Личность — стиль поведения, как вас видят окружающие"
        BIRTHDAY = "🟩 День рождения — врождённые дары, проявления спонтанности"

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

    # ===== Утилиты для форматирования ошибок =====
    @staticmethod
    def format_error(error_message: str, context: str = None) -> str:
        """Форматирует ошибку с контекстом."""
        if context:
            return f"{M.ERRORS.PREFIX}{error_message}\n{context}"
        return f"{M.ERRORS.PREFIX}{error_message}"
    
    @staticmethod
    def format_error_details(base_error: str, details: str) -> str:
        """Форматирует ошибку с подробностями."""
        return f"{base_error}\nПодробности: {details}"
    
    @staticmethod
    def format_api_error(status: int, reason: str) -> str:
        """Форматирует ошибку API."""
        return f"{M.ERRORS.API_ERROR} {status}: {reason}"
    
    @staticmethod
    def format_network_error(error: str) -> str:
        """Форматирует сетевую ошибку."""
        return f"{M.ERRORS.NETWORK_ERROR}: {error}"
    
    @staticmethod
    def is_ai_error(response: str) -> bool:
        """Проверяет, является ли ответ AI ошибкой."""
        if not isinstance(response, str):
            return False
        return (
            response.startswith("❌") or 
            response == M.ERRORS.AI_GENERIC or
            response == M.ERRORS.AI_EMPTY or
            response == M.ERRORS.AI_NO_KEY or
            response == M.ERRORS.AI_UNEXPECTED
        )
    
    @staticmethod
    async def send_auto_delete_error(update, context, error_text: str, delete_after: float = 5.0, **kwargs):
        """Отправляет сообщение об ошибке с автоматическим удалением."""
        from .progress import MessageManager
        msg_manager = MessageManager(context)
        return await msg_manager.send_error_and_track(update, error_text, delete_after, **kwargs)