# Логика проекта (без UI)

Этот проект теперь содержит только логику расчетов и API, без визуальных элементов. UI будет встраиваться через Construct 3.

## Что осталось:

### Python компоненты:
- `bot.py` - Telegram бот
- `api.py` - FastAPI сервер для AI анализа
- `calc/` - Нумерологические расчеты
- `intelligence/` - AI анализ
- `flows/` - Потоки взаимодействия с пользователями
- `output/` - Генерация отчетов
- `helpers/` - Вспомогательные функции

### JavaScript логика (src/):
- `src/utils/calculations.js` - Нумерологические расчеты
- `src/utils/validation.js` - Валидация данных
- `src/features/aiAnalysis.js` - AI анализ
- `src/api/ai.js` - AI API клиент
- `src/api/http.js` - HTTP клиент

## Что удалено:
- ❌ `index.html` - HTML интерфейс
- ❌ `src/styles/` - CSS стили
- ❌ `src/components/` - UI компоненты
- ❌ `src/app.js` - Главное приложение с UI
- ❌ `src/utils/ui.js` - UI утилиты
- ❌ `src/utils/navigation.js` - Навигация UI
- ❌ `src/features/storage.js` - Хранение UI данных
- ❌ `server.js` - HTTP сервер для UI
- ❌ `package.json` - Node.js зависимости
- ❌ `node_modules/` - Node.js пакеты
- ❌ `phaser-editor-project/` - Phaser проекты
- ❌ `interface/` - Telegram bot UI интерфейсы

## Использование:

### Для Telegram бота:
```bash
make run  # Запуск бота
make api  # Запуск API сервера
```

### Для интеграции с Construct 3:
Используйте файлы из папки `src/` для встраивания логики в ваш Construct 3 проект.

Основные классы:
- `Calculations` - для всех нумерологических расчетов
- `Validation` - для валидации входных данных
- `AIAnalysis` - для AI анализа
- `AIApi` - для работы с AI API
