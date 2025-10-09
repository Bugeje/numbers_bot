# Разбор `input_flow.gd`

Ниже приведён список строк с пояснениями. Чтобы увидеть зелёный цвет комментария, откройте файл в предпросмотре Markdown (например, в VS Code нажмите `Ctrl+Shift+V`).

| Код | Комментарий |
| --- | --- |
| <code>extends RefCounted</code> | <span style="color:green"># создаём вспомогательный объект без узла на сцене</span> |
| <code>class_name InputFlow</code> | <span style="color:green"># делаем класс доступным по имени для других скриптов</span> |
| <code>enum Step { NAME, DATE, RESULT }</code> | <span style="color:green"># перечисляем этапы мастера: имя → дата → результат</span> |
| <code>const NAME_ERROR_SHORT := "Введите минимум имя и фамилию."</code> | <span style="color:green"># фраза для предупреждения: указано меньше двух слов</span> |
| <code>const NAME_ERROR_INVALID := "Имя может содержать только буквы, дефис или апостроф."</code> | <span style="color:green"># подсказка, если в имени есть неподходящие символы</span> |
| <code>const NAME_OK := "Ок"</code> | <span style="color:green"># короткое сообщение об успехе для имени</span> |
| <code>const DATE_ERROR := "Дата должна быть в формате ДД.ММ.ГГГГ."</code> | <span style="color:green"># сообщение об ошибке формата даты</span> |
| <code>const DATE_OK := "Ок"</code> | <span style="color:green"># подтверждение корректной даты</span> |
| <code>var _date_regex := RegEx.new()</code> | <span style="color:green"># создаём регулярное выражение для проверки даты</span> |
| <code>var _name_part_regex := RegEx.new()</code> | <span style="color:green"># регулярка для проверки каждого слова в имени</span> |
| <code>var current_step: Step = Step.NAME</code> | <span style="color:green"># по умолчанию ждём ввод имени</span> |
| <code>var full_name := ""</code> | <span style="color:green"># сюда попадёт нормализованное ФИО</span> |
| <code>var birthdate := ""</code> | <span style="color:green"># здесь будет отформатированная дата рождения</span> |
| <code>func _init() -> void:</code> | <span style="color:green"># на этапе создания готовим шаблоны проверки</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;_date_regex.compile(r"^(0[1-9]|[12]\d|3[01])\.(0[1-9]|1[0-2])\.(19\d{2}|20\d{2})$")</code> | <span style="color:green"># разрешаем даты вида ДД.ММ.ГГГГ и ограничиваем диапазон</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;_name_part_regex.compile(r"^[\p{L}][\p{L}\-']+$")</code> | <span style="color:green"># разрешаем буквы, дефис и апостроф в словах имени</span> |
| <code>func reset() -> void:</code> | <span style="color:green"># сбрасываем прогресс мастера</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;current_step = Step.NAME</code> | <span style="color:green"># возвращаемся к шагу ввода имени</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;full_name = ""</code> | <span style="color:green"># стираем ранее сохранённое имя</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;birthdate = ""</code> | <span style="color:green"># стираем сохранённую дату</span> |
| <code>func submit_name(raw: String) -> Dictionary:</code> | <span style="color:green"># проверяем введённое имя</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;var sanitized := raw.strip_edges()</code> | <span style="color:green"># удаляем пробелы по краям строки</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;var parts: PackedStringArray = sanitized.split(" ", false)</code> | <span style="color:green"># разбиваем имя на отдельные слова</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;if parts.size() < 2:</code> | <span style="color:green"># требуется минимум два слова: имя и фамилия</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return { "ok": false, "message": NAME_ERROR_SHORT }</code> | <span style="color:green"># если меньше — сообщаем об ошибке</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;for part in parts:</code> | <span style="color:green"># по очереди проверяем каждую часть имени</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if _name_part_regex.search(part) == null:</code> | <span style="color:green"># если символы не подходят</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return { "ok": false, "message": NAME_ERROR_INVALID }</code> | <span style="color:green"># сообщаем о недопустимых символах</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;full_name = " ".join(parts)</code> | <span style="color:green"># склеиваем слова обратно в нормализованное ФИО</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;current_step = Step.DATE</code> | <span style="color:green"># переключаемся на этап с датой</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;return { "ok": true, "message": NAME_OK, "step": current_step, "value": full_name }</code> | <span style="color:green"># возвращаем успешный результат</span> |
| <code>func submit_birthdate(raw: String) -> Dictionary:</code> | <span style="color:green"># проверяем введённую дату рождения</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;var sanitized := raw.strip_edges()</code> | <span style="color:green"># убираем пробелы вокруг даты</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;if _date_regex.search(sanitized) == null:</code> | <span style="color:green"># проверяем формат</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return { "ok": false, "message": DATE_ERROR }</code> | <span style="color:green"># если не совпадает — возвращаем ошибку</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;birthdate = sanitized</code> | <span style="color:green"># сохраняем проверенную дату</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;current_step = Step.RESULT</code> | <span style="color:green"># переходим к финальному шагу</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;return { "ok": true, "message": DATE_OK, "step": current_step, "value": birthdate }</code> | <span style="color:green"># сообщаем об успехе и передаём дату</span> |
| <code>func get_payload() -> Dictionary:</code> | <span style="color:green"># формируем итоговый набор данных</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;return { "full_name": full_name, "birthdate": birthdate }</code> | <span style="color:green"># отдаём имя и дату, готовые для API</span> |

**Главная идея:** InputFlow действует как «пропускной пункт» — пропускает к API только те данные, где имя состоит минимум из двух слов, дата соответствует формату ДД.ММ.ГГГГ, а результат удобно упакован в словарь.
