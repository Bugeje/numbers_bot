# Разбор `profile_service.gd`

| Код | Комментарий |
| --- | --- |
| <code>extends Node</code> | <span style="color:green"># создаём узел, который можно добавить на сцену</span> |
| <code>class_name ProfileService</code> | <span style="color:green"># регистрируем имя класса для удобного доступа</span> |
| <code>## Сервис оборачивает HTTPRequest, отправляет запросы к API и транслирует сигналы.</code> | <span style="color:green"># общий комментарий автора</span> |
| <code>signal request_started(kind: String)</code> | <span style="color:green"># оповещение, что запрос отправлен</span> |
| <code>signal request_finished(kind: String)</code> | <span style="color:green"># оповещение, что запрос завершён</span> |
| <code>signal profile_ready(profile: Dictionary)</code> | <span style="color:green"># сигнал с данными профиля</span> |
| <code>signal analysis_ready(profile: Dictionary, analysis: String)</code> | <span style="color:green"># сигнал с профилем и текстом анализа</span> |
| <code>signal request_failed(kind: String, message: String)</code> | <span style="color:green"># сигнал об ошибке с описанием</span> |
| <code>@export var profile_endpoint: String = "http://127.0.0.1:8000/profile"</code> | <span style="color:green"># адрес эндпоинта для расчёта профиля</span> |
| <code>@export var analysis_endpoint: String = "http://127.0.0.1:8000/profile/analysis"</code> | <span style="color:green"># адрес эндпоинта для анализа с AI</span> |
| <code>var _http: HTTPRequest</code> | <span style="color:green"># ссылка на узел HTTPRequest</span> |
| <code>var _busy := false</code> | <span style="color:green"># флаг: сейчас идёт запрос</span> |
| <code>var _current_request := ""</code> | <span style="color:green"># запоминаем тип активного запроса</span> |
| <code></code> | <span style="color:green"></span> |
| <code>func setup(http_node: HTTPRequest) -> void:</code> | <span style="color:green"># привязываем внешний HTTPRequest и подписываемся на сигнал</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;_clear_connections()</code> | <span style="color:green"># на всякий случай отключаем старые соединения</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;_http = http_node</code> | <span style="color:green"># сохраняем ссылку на переданный узел</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;if _http:</code> | <span style="color:green"># проверяем, что узел есть</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_http.request_completed.connect(_on_request_completed)</code> | <span style="color:green"># подписываемся на событие завершения запроса</span> |
| <code></code> | <span style="color:green"></span> |
| <code>func is_ready() -> bool:</code> | <span style="color:green"># проверяем, привязан ли HTTPRequest</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;return _http != null</code> | <span style="color:green"># true, если узел установлен</span> |
| <code></code> | <span style="color:green"></span> |
| <code>func is_busy() -> bool:</code> | <span style="color:green"># сообщаем, идёт ли сейчас запрос</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;return _busy</code> | <span style="color:green"># true, если сервис занят</span> |
| <code></code> | <span style="color:green"></span> |
| <code>func request_profile(full_name: String, birthdate: String) -> void:</code> | <span style="color:green"># отправляем запрос на построение профиля</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;var payload := {</code> | <span style="color:green"># собираем тело запроса</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"full_name": full_name,</code> | <span style="color:green"># передаём имя</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"birthdate": birthdate,</code> | <span style="color:green"># передаём дату рождения</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;}</code> | <span style="color:green"># закрываем словарь</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;_send_request("profile", profile_endpoint, payload)</code> | <span style="color:green"># отправляем POST-запрос на нужный URL</span> |
| <code></code> | <span style="color:green"></span> |
| <code>func request_analysis(full_name: String, birthdate: String) -> void:</code> | <span style="color:green"># запрашиваем профиль вместе с AI-анализом</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;var payload := {</code> | <span style="color:green"># тело запроса такое же</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"full_name": full_name,</code> | <span style="color:green"># имя</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"birthdate": birthdate,</code> | <span style="color:green"># дата</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;}</code> | <span style="color:green"># закрываем словарь</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;_send_request("analysis", analysis_endpoint, payload)</code> | <span style="color:green"># отправляем запрос на другой эндпоинт</span> |
| <code></code> | <span style="color:green"></span> |
| <code>func _clear_connections() -> void:</code> | <span style="color:green"># защищаемся от повторного подключения сигналов</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;if _http and _http.request_completed.is_connected(_on_request_completed):</code> | <span style="color:green"># проверяем, что сигнал уже был подключён</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_http.request_completed.disconnect(_on_request_completed)</code> | <span style="color:green"># отключаем старое соединение</span> |
| <code></code> | <span style="color:green"></span> |
| <code>func _send_request(kind: String, url: String, payload: Dictionary) -> void:</code> | <span style="color:green"># общий метод отправки POST-запроса</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;if _busy:</code> | <span style="color:green"># если уже идёт запрос</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;emit_signal("request_failed", kind, "Загрузка уже выполняется.")</code> | <span style="color:green"># сообщаем об ошибке и выходим</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | <span style="color:green"># прерываем выполнение</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;if not _http:</code> | <span style="color:green"># если HTTPRequest не привязан</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;emit_signal("request_failed", kind, "HTTPRequest не привязан к сервису.")</code> | <span style="color:green"># сигнализируем об ошибке конфигурации</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | <span style="color:green"># выходим</span> |
| <code></code> | <span style="color:green"></span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;var body := JSON.stringify(payload)</code> | <span style="color:green"># преобразуем словарь в строку JSON</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;var err := _http.request(url, ["Content-Type: application/json"], HTTPClient.METHOD_POST, body)</code> | <span style="color:green"># отправляем POST-запрос с нужными заголовками</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;if err != OK:</code> | <span style="color:green"># если Godot вернул ошибку на этапе отправки</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;emit_signal("request_failed", kind, "Не удалось отправить запрос: %s" % str(err))</code> | <span style="color:green"># уведомляем UI и выходим</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | <span style="color:green"># прекращаем выполнение</span> |
| <code></code> | <span style="color:green"></span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;_busy = true</code> | <span style="color:green"># помечаем сервис занятым</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;_current_request = kind</code> | <span style="color:green"># сохраняем тип текущего запроса</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;emit_signal("request_started", kind)</code> | <span style="color:green"># сообщаем подписчикам, что запрос начался</span> |
| <code></code> | <span style="color:green"></span> |
| <code>func _on_request_completed(result: int, code: int, _headers: PackedStringArray, body: PackedByteArray) -> void:</code> | <span style="color:green"># колбэк, который вызывается при завершении HTTP-запроса</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;var kind := _current_request</code> | <span style="color:green"># сохраняем тип запроса до очистки</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;_current_request = ""</code> | <span style="color:green"># сбрасываем информацию о запросе</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;_busy = false</code> | <span style="color:green"># сервис снова свободен</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;emit_signal("request_finished", kind)</code> | <span style="color:green"># уведомляем, что запрос завершён</span> |
| <code></code> | <span style="color:green"></span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;if result != HTTPRequest.RESULT_SUCCESS:</code> | <span style="color:green"># Godot сообщил об ошибке соединения</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;emit_signal("request_failed", kind, "Ошибка сети: %d" % result)</code> | <span style="color:green"># пересылаем код ошибки подписчикам</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | <span style="color:green"># дальше обработка не требуется</span> |
| <code></code> | <span style="color:green"></span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;var text: String = body.get_string_from_utf8()</code> | <span style="color:green"># читаем тело ответа как текст</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;var parsed: Variant = JSON.parse_string(text)</code> | <span style="color:green"># пытаемся разобрать JSON</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;if typeof(parsed) != TYPE_DICTIONARY:</code> | <span style="color:green"># проверяем, что сервер прислал объект</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;emit_signal("request_failed", kind, "Неверный формат ответа: %s" % text)</code> | <span style="color:green"># уведомляем об ошибке формата</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | <span style="color:green"># прекращаем обработку</span> |
| <code></code> | <span style="color:green"></span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;var data: Dictionary = parsed</code> | <span style="color:green"># приводим Variant к словарю</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;if code != 200:</code> | <span style="color:green"># если сервер вернул ошибку</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;var detail: String = str(data.get("detail", text))</code> | <span style="color:green"># достаём пояснение к ошибке</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;emit_signal("request_failed", kind, "Ошибка %d: %s" % [code, detail])</code> | <span style="color:green"># отправляем сообщение подписчикам</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | <span style="color:green"># дальше не продолжаем</span> |
| <code></code> | <span style="color:green"></span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;if kind == "analysis" or data.has("analysis"):</code> | <span style="color:green"># если ответ содержит анализ</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;var analysis_text: String = str(data.get("analysis", ""))</code> | <span style="color:green"># берём текст анализа</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;var profile_variant: Variant = data.get("profile", {})</code> | <span style="color:green"># достаём вложенный профиль</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;var profile_data: Dictionary = {}</code> | <span style="color:green"># подготавливаем словарь для профиля</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if typeof(profile_variant) == TYPE_DICTIONARY:</code> | <span style="color:green"># убеждаемся, что профиль действительно словарь</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;profile_data = profile_variant</code> | <span style="color:green"># приводим к нужному типу</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;emit_signal("analysis_ready", profile_data, analysis_text)</code> | <span style="color:green"># отправляем сигнал с профилем и анализом</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;else:</code> | <span style="color:green"># иначе это просто результат профиля</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;emit_signal("profile_ready", data)</code> | <span style="color:green"># передаём словарь профиля подписчикам</span> |

**Итог:** `ProfileService` принимает HTTPRequest, умеет отправлять запросы профиля и анализа, а также аккуратно разруливает ошибки и события, чтобы остальной UI мог реагировать на результат.
