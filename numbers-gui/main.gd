extends Control

# Получаем ссылки на элементы интерфейса
@onready var date_input: LineEdit = $DateLineEdit
@onready var name_input: LineEdit = $NameLineEdit
@onready var date_button: Button = $DateButton
@onready var name_button: Button = $NameButton
@onready var profile_button: Button = $ProfileButton
@onready var date_label: Label = $DateLabel
@onready var name_label: Label = $NameLabel
@onready var result_label: Label = $ResultLabel

const PROFILE_ENDPOINT := "http://127.0.0.1:8001/profile"  # замените на адрес вашего сервера

var date_regex := RegEx.new()
var name_regex := RegEx.new()
var http_request: HTTPRequest = null

func _ready() -> void:
	# Настраиваем обработчики и регулярные выражения
	var date_err := date_regex.compile("^\\d{2}\\.\\d{2}\\.\\d{4}$")
	if date_err != OK:
		push_warning("Не удалось скомпилировать регулярное выражение даты")
	var name_err := name_regex.compile("^[А-Яа-яЁё]+$")
	if name_err != OK:
		push_warning("Не удалось скомпилировать регулярное выражение ФИО")
	date_button.pressed.connect(_on_date_button_pressed)
	name_button.pressed.connect(_on_name_button_pressed)
	profile_button.pressed.connect(_on_ProfileButton_pressed)

	http_request = get_node_or_null("HTTPRequest")
	if http_request:
		http_request.request_completed.connect(_on_HTTPRequest_request_completed)
	else:
		push_warning("Узел HTTPRequest не найден. Проверьте сцену.")

func _on_date_button_pressed() -> void:
	# Проверяем дату перед выводом
	var text := date_input.text.strip_edges()
	if date_regex.search(text):
		date_label.text = "Введённая дата: " + text
	else:
		date_label.text = "Ошибка: введите дату в формате ДД.ММ.ГГГГ"

func _on_name_button_pressed() -> void:
	# Проверяем ФИО: минимум два слова и только буквы
	var text := name_input.text.strip_edges()
	var parts: Array = text.split(" ", false)
	if parts.size() < 2:
		name_label.text = "Ошибка: нужно минимум Имя и Фамилия"
		return
	for part in parts:
		if name_regex.search(part) == null:
			name_label.text = "Ошибка: допустимы только буквы"
			return
	name_label.text = "ФИО корректно: " + text

func _on_ProfileButton_pressed() -> void:
	# Отправляем профиль на сервер FastAPI
	if http_request == null:
		result_label.text = "Ошибка: узел HTTPRequest не найден"
		return
	if http_request.is_requesting():
		result_label.text = "Запрос уже выполняется"
		return

	var payload := {
		"full_name": name_input.text.strip_edges(),
		"birthdate": date_input.text.strip_edges()
	}
	var json_body := JSON.stringify(payload)
	var headers := PackedStringArray(["Content-Type: application/json"])
	var err := http_request.request(PROFILE_ENDPOINT, headers, HTTPClient.METHOD_POST, json_body)
	if err != OK:
		result_label.text = "Ошибка: не удалось отправить запрос (код %d)" % err
	else:
		result_label.text = "Отправляем запрос на сервер..."

func _parse_json(body_text: String) -> Dictionary:
	var parser := JSON.new()
	var error := parser.parse(body_text)
	if error == OK:
		var parsed: Variant = parser.data
		if parsed is Dictionary:
			return parsed
	return {}

func _on_HTTPRequest_request_completed(result: int, response_code: int, _headers: PackedStringArray, body: PackedByteArray) -> void:
	# Обрабатываем ответ сервера FastAPI
	if result != HTTPRequest.RESULT_SUCCESS:
		result_label.text = "Ошибка сети: код %d" % result
		return

	var body_text := body.get_string_from_utf8()
	if response_code == 200:
		var data: Dictionary = _parse_json(body_text)
		if data.size() > 0:
			result_label.text = "Жизненный путь: %s\nДень рождения: %s\nВыражение: %s\nДуша: %s\nЛичность: %s" % [
				str(data.get("life_path", "")),
				str(data.get("birthday", "")),
				str(data.get("expression", "")),
				str(data.get("soul", "")),
				str(data.get("personality", ""))
			]
		else:
			result_label.text = "Ошибка: не удалось разобрать ответ"
	else:
		result_label.text = "Ошибка сервера %d: %s" % [response_code, body_text]
