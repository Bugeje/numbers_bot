extends Node
class_name ProfileService

## Обвязка над HTTPRequest, которая отправляет запросы к API и транслирует сигналы.

signal request_started(kind: String)
signal request_finished(kind: String)
signal profile_ready(profile: Dictionary)
signal analysis_ready(profile: Dictionary, analysis: String)
signal request_failed(kind: String, message: String)

@export var profile_endpoint: String = "http://127.0.0.1:8000/profile" ## Базовый URL для расчёта профиля.
@export var analysis_endpoint: String = "http://127.0.0.1:8000/profile/analysis" ## URL для профиля с AI‑анализом.

var _http: HTTPRequest
var _busy := false
var _current_request := ""


func setup(http_node: HTTPRequest) -> void:
	## Привязываем внешний HTTPRequest и подписываемся на сигнал завершения.
	_clear_connections()
	_http = http_node
	if _http:
		_http.request_completed.connect(_on_request_completed)


func is_ready() -> bool:
	return _http != null


func is_busy() -> bool:
	return _busy


func request_profile(full_name: String, birthdate: String) -> void:
	## Запрашиваем расчёт профиля без анализа.
	var payload := {
		"full_name": full_name,
		"birthdate": birthdate,
	}
	_send_request("profile", profile_endpoint, payload)


func request_analysis(full_name: String, birthdate: String) -> void:
	## Запрашиваем расчёт профиля и AI‑анализа.
	var payload := {
		"full_name": full_name,
		"birthdate": birthdate,
	}
	_send_request("analysis", analysis_endpoint, payload)


func _clear_connections() -> void:
	## Избегаем дублирующих соединений при повторных настройках.
	if _http and _http.request_completed.is_connected(_on_request_completed):
		_http.request_completed.disconnect(_on_request_completed)


func _send_request(kind: String, url: String, payload: Dictionary) -> void:
	## Общий помощник для отправки POST‑запросов.
	if _busy:
		emit_signal("request_failed", kind, "Загрузка уже выполняется.")
		return
	if not _http:
		emit_signal("request_failed", kind, "HTTPRequest не привязан к сервису.")
		return

	var body := JSON.stringify(payload)
	var err := _http.request(url, ["Content-Type: application/json"], HTTPClient.METHOD_POST, body)
	if err != OK:
		emit_signal("request_failed", kind, "Не удалось отправить запрос: %s" % str(err))
		return

	_busy = true
	_current_request = kind
	emit_signal("request_started", kind)


func _on_request_completed(result: int, code: int, _headers: PackedStringArray, body: PackedByteArray) -> void:
	## Обрабатываем финал запроса, разбираем JSON и уведомляем слушателей.
	var kind := _current_request
	_current_request = ""
	_busy = false
	emit_signal("request_finished", kind)

	if result != HTTPRequest.RESULT_SUCCESS:
		emit_signal("request_failed", kind, "Ошибка сети: %d" % result)
		return

	var text := body.get_string_from_utf8()
	var parsed := JSON.parse_string(text)
	if typeof(parsed) != TYPE_DICTIONARY:
		emit_signal("request_failed", kind, "Неверный формат ответа: %s" % text)
		return

	var data: Dictionary = parsed
	if code != 200:
		var detail := data.get("detail", text)
		emit_signal("request_failed", kind, "Ошибка %d: %s" % [code, detail])
		return

	if kind == "analysis" or data.has("analysis"):
		var analysis_text := str(data.get("analysis", ""))
		var profile_data := data.get("profile", {})
		if typeof(profile_data) != TYPE_DICTIONARY:
			profile_data = {}
		emit_signal("analysis_ready", profile_data, analysis_text)
	else:
		emit_signal("profile_ready", data)
