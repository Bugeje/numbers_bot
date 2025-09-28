# Numbers Core

`numbers_core` — модуль на Python для расчёта нумерологических профилей и генерации текстовых интерпретаций с помощью AI-клиентов. Его можно использовать в Telegram-ботах, десктопных приложениях или любых других интеграциях, где нужна автоматическая интерпретация чисел даты рождения и ФИО.

## Возможности

- Расчёт ключевых чисел (путь судьбы, число дня рождения, число экспрессии, души и личности).
- Удобные функции-адаптеры: расчёт профиля, генерация текстового разбора, получение структурированных данных.
- Возможность подменять AI-клиента на любой другой движок (OpenAI, локальные модели и т. п.).
- Готовая схема тестирования и примеры использования.

## Требования

- Python 3.10 или новее.
- Базовая подготовленная среда: виртуальное окружение Python и установленный pip.

## Установка

```bash
pip install -e .
```

> Можно использовать `pip install .`, если не планируете локальные правки кода.

## Быстрый старт

```python
from numbers_core import ProfileInput, run

result = run(ProfileInput(name="Иван Иванов", birthdate="1990-01-01"))
print(result["profile"])            # расчёт чисел и их значения
print(result["analysis"]["text"])  # текст, сгенерированный AI-клиентом
```

- `profile` — словарь с ключами `life_path`, `birthday`, `expression`, `soul`, `personality`.
- `analysis` — словарь с полем `text`. В примерах используется заглушка `MockAIClient`.

## Минимальный расчёт без AI

```python
from numbers_core.calc import calculate_core_profile

profile = calculate_core_profile("Иван Иванов", "01.01.1990")
```

Дополнительные функции доступны в пакете `numbers_core.calc` (суммы, редукция, подсчёт букв и т. д.) и экспортируются через `numbers_core/calc/__init__.py`.

## Подключение собственного AI-клиента

```python
from numbers_core import ProfileInput, run
from numbers_core.intelligence.engine import AIClient

class MyAIClient(AIClient):
    def generate(self, prompt: str) -> str:
        return "Ваш кастомный ответ"

result = run(ProfileInput(name="Иван Иванов", birthdate="1990-01-01"), ai=MyAIClient())
```

По умолчанию используется `MockAIClient`, который подходит для разработки и тестов.

## Структура репозитория

- `numbers_core/calc` — функции нумерологических расчётов.
- `numbers_core/core` — бизнес-логика: оркестратор и взаимодействие с AI.
- `numbers_core/intelligence` — интерфейсы и реализации AI-клиентов.
- `numbers_core/tests` — модульные тесты.
- `numbers-gui` — экспериментальный интерфейс на Godot 4 для ручного ввода данных.

## Тесты

```bash
python -m pytest numbers_core/tests
```

Тесты можно запускать как из IDE, так и из командной строки. Добавляйте дополнительные сценарии в `numbers_core/tests` по мере развития проекта.

## Интерфейс Godot (`numbers-gui`)

Скрипт `numbers-gui/main.gd` реализует простую форму на Godot 4:

- Два `LineEdit`: `DateLineEdit` для даты и `NameLineEdit` для ФИО.
- Три кнопки: `DateButton`, `NameButton`, `ProfileButton` (для отправки данных на сервер).
- Три `Label`: `DateLabel`, `NameLabel`, `ResultLabel`.
- Узел `HTTPRequest`, который отправляет POST-запрос на FastAPI-сервер и получает JSON с расчётами.

### Как собрать сцену

1. Создайте сцену с корневым узлом `Control` и привяжите к нему скрипт `main.gd`.
2. Добавьте дочерние узлы с именами, соответствующими переменным в скрипте (пути `$…` должны совпасть).
3. Подключите сигнал `request_completed` от узла `HTTPRequest` к методу `_on_HTTPRequest_request_completed` и сигнал `pressed` от `ProfileButton` к `_on_ProfileButton_pressed` (через Inspector → Node → Signals).
4. Замените `PROFILE_ENDPOINT` в коде на адрес вашего сервера.
5. Запустите сцену: проверки даты и ФИО работают локально, кнопка «Профиль» отправляет данные и отображает ответ сервера.

## Вариант для мобильных клиентов: FastAPI + HTTP

На Android/iOS нет Python-интерпретатора, поэтому расчёты выполняются на сервере. Минимальный пример сервера и клиента уже лежит в репозитории:

- `api.py` — FastAPI-приложение с эндпойнтом `POST /profile`, который вызывает `calculate_core_profile` и возвращает JSON с ключевыми числами.
- `requirements.txt` — зависимости сервера (`fastapi`, `uvicorn`, `pydantic>=2,<3`).
- Godot-скрипт (`numbers-gui/main.gd`) отправляет JSON `{"full_name": ..., "birthdate": ...}` через узел `HTTPRequest` и отображает полученные значения.

### Запуск сервера

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python api.py
```

Сервер стартует на `http://0.0.0.0:8000`, эндпойнт `POST /profile` принимает JSON вида:

```json
{
  "full_name": "Иван Иванов",
  "birthdate": "26.09.2025"
}
```

Ответ содержит поля `life_path`, `birthday`, `expression`, `soul`, `personality`, которые клиент Godot выводит в `ResultLabel`.

## Обратная связь

Предложения и вопросы можно отправлять через issue или pull request.
