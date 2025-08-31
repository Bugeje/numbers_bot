# 📨 Система сообщений

Централизованная система сообщений Numbers Bot для унификации интерфейса и упрощения локализации.

## Концепция

Все тексты, названия файлов и сообщения вынесены в централизованные константы в [helpers/messages.py](file:///home/celina/numbers_bot/helpers/messages.py):
- `BTN` - кнопки интерфейса
- `FILENAMES` - названия PDF файлов  
- `M` - все остальные сообщения

Это позволяет:
- ✅ Менять тексты в одном месте
- ✅ Обеспечить единый стиль
- ✅ Упростить локализацию
- ✅ Избежать дублирования строк

## Структура

### Кнопки (`BTN`)
Интерфейсные кнопки:
```python
BTN.CORE = "📄 Ядро личности"
BTN.MONTHS = "📆 Анализ месяцев"
BTN.RESTART = "🔁 Старт"
# и т.д.
```

### Названия файлов (`FILENAMES`)
Централизованные названия PDF файлов:
```python
FILENAMES.CORE_PROFILE = "Ядро_личности.pdf"
FILENAMES.MONTHS = "Анализ_месяцев.pdf"
FILENAMES.BRIDGES = "Анализ_мостов.pdf"
FILENAMES.CALENDAR_DAYS = "Календарь_дней.pdf"
# и т.д.
```

### Основные сообщения (`M`)

#### Прогресс (`M.PROGRESS`)
Сообщения о ходе выполнения операций:
- `CALC_LABEL` - расчет профиля
- `AI_LABEL` - генерация AI-анализа
- `FAIL` - ошибка операции

#### Подсказки (`M.HINTS`)
Интерактивные подсказки пользователю:
- `ASK_NAME_FULL` - приветствие и запрос имени
- `ASK_BIRTHDATE_COMPACT` - запрос даты рождения
- `ASK_PARTNER_NAME`, `ASK_PARTNER_BIRTHDATE` - запросы данных партнера
- `MISSING_BASIC_DATA` - предупреждения об отсутствии данных
- `NEXT_STEP` - подсказка для следующего шага

#### Ошибки (`M.ERRORS`)
Унифицированные сообщения об ошибках:
- Общие: `PREFIX`, `GENERIC_ERROR`
- Данные: `NAME_PREFIX`, `DATE_PREFIX`
- Расчеты: `CALC_PROFILE`
- AI: `AI_GENERIC`, `AI_NO_KEY`, `AI_EMPTY`
- Сеть: `NETWORK_ERROR`, `API_ERROR`

#### Описания календаря (`M.CALENDAR_LEGENDS`)
Описания цветных меток в календаре:
- `LIFE_PATH` - жизненный путь (🟥)
- `EXPRESSION` - выражение (🟦)
- `SOUL` - душа (🟣)
- `PERSONALITY` - личность (🟨)
- `BIRTHDAY` - день рождения (🟩)

## Утилитарные функции

### Форматирование ошибок
```python
M.format_error("text", "context")              # Общие ошибки
M.format_error_details(base_error, details)     # Ошибки с подробностями
M.format_api_error(404, "Not Found")           # API ошибки  
M.format_network_error("timeout")              # Сетевые ошибки
```

### Проверка AI-ошибок
```python
M.is_ai_error(response)  # Проверяет, является ли ответ AI ошибкой
```

### Автоудаление ошибок
```python
# Отправляет сообщение об ошибке с автоудалением
M.send_auto_delete_error(update, context, "Текст ошибки", delete_after=5.0)

# Поддерживает все аргументы reply_text
M.send_auto_delete_error(
    update, context, 
    "*Ошибка в формате Markdown*",
    parse_mode="Markdown",
    delete_after=3.0
)
```

## Принципы использования

### ✅ Правильно:
```python
# Обычные сообщения
await msg_manager.send_and_track(update, M.HINTS.NEXT_STEP)

# Сообщения об ошибках (автоудаление)
await M.send_auto_delete_error(update, context, M.HINTS.MISSING_BASIC_DATA)
await M.send_auto_delete_error(update, context, M.format_error_details(M.ERRORS.CALC_PROFILE, str(e)))

# Названия файлов
await update.message.reply_document(
    document=pdf_file, filename=FILENAMES.CORE_PROFILE
)

# Константы кнопок в regex
filters.Regex(f"^{re.escape(BTN.CALENDAR_DAYS)}$")

# Описания календаря
legend = {
    "match-life_path": M.CALENDAR_LEGENDS.LIFE_PATH,
    "match-soul": M.CALENDAR_LEGENDS.SOUL
}

# Проверка AI ошибок
if M.is_ai_error(ai_response):
    # обработка ошибки
```

### ❌ Неправильно:
```python
# Ошибки, которые не удаляются
await update.message.reply_text("⚠️ Не хватает данных...")  # жестко закодировано + не удаляется
await update.message.reply_text(f"❌ Ошибка: {e}")        # дублирование + не удаляется

# Названия файлов жестко в коде
await update.message.reply_document(
    document=pdf_file, filename="Ядро_личности.pdf"  # дублирование
)

# Жестко закодированные regex
filters.Regex("📅 Календарь дней")  # жестко в коде

# Описания календаря жестко в коде
legend = {
    "match-life_path": "🟥 Жизненный путь — ...",  # дублирование
}

if ai_response.startswith("❌"):                           # хрупкая проверка
```

## Автоматическое скрытие сообщений

Система использует `MessageManager` для автоматического удаления предыдущих служебных сообщений при переходе к новым этапам, что обеспечивает чистый интерфейс.

### ⚠️ ВАЖНО: Навигационные клавиатуры НЕ должны отслеживаться для удаления

Клавиатуры с кнопками навигации (например, `build_after_analysis_keyboard()`) **НЕ ДОЛЖНЫ** отправляться через `msg_manager.send_and_track()`, так как это приведет к их удалению при следующем `cleanup_tracked_messages()`.

```python
# ✅ ПРАВИЛЬНО - клавиатура остается на экране
await update.effective_message.reply_text(
    M.HINTS.NEXT_STEP, reply_markup=build_after_analysis_keyboard()
)

# ❌ НЕПРАВИЛЬНО - клавиатура исчезнет при следующей очистке
await msg_manager.send_and_track(
    update, M.HINTS.NEXT_STEP, reply_markup=build_after_analysis_keyboard()
)
```

### Автоудаление сообщений об ошибках

Все сообщения об ошибках автоматически удаляются через 5 секунд с помощью функции:
```python
# Отправляет сообщение об ошибке с автоудалением
await M.send_auto_delete_error(update, context, "Текст ошибки", delete_after=5.0)

# Поддерживает все аргументы reply_text (parse_mode, reply_markup и т.д.)
await M.send_auto_delete_error(
    update, context, 
    "*Ошибка в формате Markdown*",
    parse_mode="Markdown",
    delete_after=3.0
)
```

Это обеспечивает:
- Информирование пользователя об ошибке
- Автоматическую очистку интерфейса
- Отсутствие накопления сообщений об ошибках

## Преимущества

1. **Централизация** - все тексты и названия файлов в одном месте
2. **Унификация** - единый стиль сообщений  
3. **Переиспользование** - одно сообщение для разных случаев
4. **Простота изменений** - правка в одном месте влияет на весь бот
5. **Типобезопасность** - автодополнение в IDE
6. **Чистый интерфейс** - автоматическое скрытие старых сообщений
7. **Автоудаление ошибок** - сообщения об ошибках не накапливаются
8. **Полная централизация** - никаких жестко закодированных строк в коде

---

## 🎉 Результат полной централизации

**ВСЕ тексты проекта централизованы!** Теперь вы можете:

- 📝 **Изменить любое сообщение** в одном месте
- 🎨 **Поменять эмодзи** для всех статусов сразу
- 🔧 **Обновить тексты кнопок** глобально
- 🌍 **Перевести весь бот** на другой язык в одном файле
- 📁 **Переименовать все PDF файлы** одной правкой