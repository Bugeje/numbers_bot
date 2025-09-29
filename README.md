# Numbers Core

`numbers_core` — библиотека на Python для расчёта числового профиля человека и генерации текстовых интерпретаций с помощью AI-клиентов. Её можно использовать отдельно, в составе Telegram-бота или вместе с Godot-клиентом из каталога `numbers-gui`.

## Возможности

- Расчёт пяти ключевых чисел (путь жизни, число судьбы, выражение, душа, личность).
- Расширяемые AI-клиенты: от мок-реализаций до интеграций с внешними API.
- Общий пайплайн `run()` c валидацией входных данных и возвратом готовой структуры.

## Требования

- Python 3.10 или новее.
- Установленный `pip`.

## Установка

```bash
pip install -e .
```

> Для production-сборки можно использовать `pip install .`.

## Быстрый пример

```python
from numbers_core import ProfileInput, run

result = run(ProfileInput(name="Иван Иванов", birthdate="1990-01-01"))
print(result["profile"])            # словарь с числами
print(result["analysis"]["text"])  # текст, который сгенерировал AI-клиент
```

- `profile` — словарь с ключами `life_path`, `birthday`, `expression`, `soul`, `personality`.
- `analysis` — словарь с ключом `text`. По умолчанию используется `MockAIClient`.

## Ручной расчёт без AI

```python
from numbers_core.calc import calculate_core_profile

profile = calculate_core_profile("Иван Иванов", "01.01.1990")
```

Функции расчёта лежат в `numbers_core/calc`, а их публичный интерфейс экспортирован из `numbers_core/calc/__init__.py`.

## Собственный AI-клиент

```python
from numbers_core import ProfileInput, run
from numbers_core.intelligence.engine import AIClient

class MyAIClient(AIClient):
    def generate(self, prompt: str) -> str:
        return "Ваш кастомный текст"

result = run(ProfileInput(name="Иван Иванов", birthdate="1990-01-01"), ai=MyAIClient())
```

`MockAIClient` можно использовать как пример и заглушку на время разработки.

## Структура репозитория

- `numbers_core/calc` — функции расчёта числовых показателей.
- `numbers_core/core` — инфраструктура пайплайна, валидация и интеграция с AI.
- `numbers_core/intelligence` — реализации AI-клиентов и связанные утилиты.
- `numbers_core/tests` — модульные тесты.
- `numbers-gui` — клиент на Godot 4 для быстрого ручного тестирования.

## Тесты

```bash
python -m pytest numbers_core/tests
```

Запускайте из виртуального окружения или IDE. Новые тесты стоит складывать в `numbers_core/tests` рядом с соответствующими модулями.

## Godot-клиент (`numbers-gui`)

Сцена `numbers-gui/main.tscn` содержит базовый интерфейс Godot 4:

- `LineEdit` поля: `DateLineEdit` (дата) и `NameLineEdit` (ФИО).
- Кнопки: `DateButton`, `NameButton`, `ProfileButton` (отправка на сервер).
- Метки: `DateLabel`, `NameLabel`, `ResultLabel`.
- Узел `HTTPRequest`, который делает POST-запросы к FastAPI-сервису.

Скрипт `main.gd`:

- Использует `@onready` для привязки узлов, включая `HTTPRequest`.
- В `_ready()` компилирует регулярные выражения и подключает сигналы.
- Хранит флаг `busy`, чтобы блокировать повторные нажатия `ProfileButton`, пока запрос выполняется.
- Подписывается на сигнал `request_completed` только один раз в `_ready()`.

### Проверка

1. Откройте сцену Godot и убедитесь, что скрипт `main.gd` назначен на корневой `Control`.
2. Проверьте, что сигнал `request_completed` у `HTTPRequest` подключён только через код — в `.tscn` он отсутствует.
3. В консоли Godot при старте должна появиться строка `READY OK`.
4. Нажатия на «Профиль» игнорируются, пока `busy` равен `true`.

## Локальный backend (FastAPI)

Файлы для API лежат рядом с корнем проекта:

- `api.py` — приложение FastAPI с маршрутом `POST /profile`, который вызывает `calculate_core_profile` и возвращает JSON.
- `requirements.txt` — зависимости (`fastapi`, `uvicorn`, `pydantic>=2,<3`).

### Запуск backend-а

**Windows (PowerShell)**

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe api.py
```

Если PowerShell заблокировал запуск, временно разрешите скрипты: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`.

**Linux/macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 api.py
```

По умолчанию сервер слушает `http://127.0.0.1:8001` и принимает JSON такого вида:

```json
{
  "full_name": "Иван Иванов",
  "birthdate": "26.09.2025"
}
```

Ответ содержит поля `life_path`, `birthday`, `expression`, `soul`, `personality`, которые выводятся в `ResultLabel`.

## Обратная связь

Создавайте issue или pull request, если нашли проблему или хотите предложить улучшение.
