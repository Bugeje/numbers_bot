extends Control

# Узлы
@onready var date_input: LineEdit = $DateLineEdit
@onready var name_input: LineEdit = $NameLineEdit
@onready var date_button: Button = $DateButton
@onready var name_button: Button = $NameButton
@onready var profile_button: Button = $ProfileButton # будем скрывать
@onready var date_label: Label = $DateLabel
@onready var name_label: Label = $NameLabel
@onready var result_label: Label = $ResultLabel
@onready var http: HTTPRequest = $HTTPRequest

# Состояния
enum Step { NAME, DATE, RESULT }
var step := Step.NAME
var busy := false

# Валидаторы
var date_regex := RegEx.new()
var name_part_regex := RegEx.new()

const PROFILE_ENDPOINT := "http://127.0.0.1:8000/profile" # замените на IP ПК
const ANALYSIS_ENDPOINT := "http://127.0.0.1:8000/profile/analysis"

# Кнопка «ИИ-анализ профиля», показывается после получения чисел
var analysis_button: Button = null
# Кэш с последним форматированным профилем, чтобы дополнять его AI-текстом
var last_profile_text := ""
# Тип активного запроса: profile/analysis — помогает корректно обновлять UI
var current_request := ""

# Контейнер для доп.кнопок под результатом
var actions_box: HBoxContainer

func _ready() -> void:
	# regex
	date_regex.compile(r"^(0[1-9]|[12]\d|3[01])\.(0[1-9]|1[0-2])\.(19\d{2}|20\d{2})$")
	name_part_regex.compile(r"^[\p{L}][\p{L}\-']+$")

	# сигналы
	name_button.pressed.connect(_on_name_confirm)
	date_button.pressed.connect(_on_date_confirm)
	http.request_completed.connect(_on_request_completed)

	# прячем старую кнопку профиля
	profile_button.visible = false

	# начальный шаг
	_show_step(Step.NAME)

func _show_step(target: Step) -> void:
	step = target

	var show_name := (step == Step.NAME)
	var show_date := (step == Step.DATE)
	var show_result := (step == Step.RESULT)

	# имя
	name_input.visible = show_name
	name_button.visible = show_name
	name_label.visible = show_name

	# дата
	date_input.visible = show_date
	date_button.visible = show_date
	date_label.visible = show_date

	# результат
	result_label.visible = show_result
	if show_result and actions_box == null:
		_create_actions_box()

func _on_name_confirm() -> void:
	var fio := name_input.text.strip_edges()
	var parts: PackedStringArray = fio.split(" ", false)
	if parts.size() < 2:
		name_label.text = "Ошибка: минимум Имя и Фамилия"
		return
	for p in parts:
		if name_part_regex.search(p) == null:
			name_label.text = "Ошибка: только буквы (можно дефис/апостроф)"
			return
	name_label.text = "Ок"
	_show_step(Step.DATE)

func _on_date_confirm() -> void:
	var ds := date_input.text.strip_edges()
	if date_regex.search(ds) == null:
		date_label.text = "Ошибка: формат ДД.ММ.ГГГГ"
		return
	date_label.text = "Ок"
	# переходим к результату и сразу шлём запрос
	_show_step(Step.RESULT)
	_send_profile_request()

# Отправляем данные на сервер, ожидаем только числовой профиль
func _send_profile_request() -> void:
	if busy:
		return
	current_request = "profile"
	var payload := {
		"full_name": name_input.text.strip_edges(),
		"birthdate": date_input.text.strip_edges()
	}
	var headers := ["Content-Type: application/json"]
	var body := JSON.stringify(payload)
	busy = true
	if analysis_button:
		analysis_button.disabled = true
	result_label.text = "Запрашиваем профиль..."
	var err := http.request(PROFILE_ENDPOINT, headers, HTTPClient.METHOD_POST, body)
	if err != OK:
		busy = false
		current_request = ""
		result_label.text = "Ошибка отправки профиля: %s" % str(err)
		if analysis_button and last_profile_text != "":
			analysis_button.disabled = false

# Повторно отправляем те же данные, но просим сервер добавить AI-анализ
func _send_analysis_request() -> void:
	if busy:
		return
	current_request = "analysis"
	var payload := {
		"full_name": name_input.text.strip_edges(),
		"birthdate": date_input.text.strip_edges()
	}
	var headers := ["Content-Type: application/json"]
	var body := JSON.stringify(payload)
	busy = true
	if analysis_button:
		analysis_button.disabled = true
	var prefix := last_profile_text
	if prefix != "":
		result_label.text = prefix + "\n\nЗапрашиваем ИИ анализ..."
	else:
		result_label.text = "Запрашиваем ИИ анализ..."
	var err := http.request(ANALYSIS_ENDPOINT, headers, HTTPClient.METHOD_POST, body)
	if err != OK:
		busy = false
		current_request = ""
		result_label.text = "Ошибка отправки анализа: %s" % str(err)
		if analysis_button:
			analysis_button.disabled = false
# Общий обработчик ответа HTTPRequest: разбираем профиль и/или текст анализа
func _on_request_completed(result: int, code: int, _h: PackedStringArray, body: PackedByteArray) -> void:
	var request_type := current_request
	current_request = ""
	busy = false
	if result != HTTPRequest.RESULT_SUCCESS:
		result_label.text = "Ошибка сети: %d" % result
		if analysis_button and request_type == "analysis":
			analysis_button.disabled = false
		return
	var text := body.get_string_from_utf8()
	var data: Variant = JSON.parse_string(text)
	if code == 200 and typeof(data) == TYPE_DICTIONARY:
		if request_type == "analysis" or data.has("analysis"):
			var analysis_text := str(data.get("analysis", ""))
			if analysis_text.strip_edges() == "":
				analysis_text = "Анализ временно недоступен."
			if data.has("profile") and typeof(data.get("profile")) == TYPE_DICTIONARY:
				last_profile_text = _format_profile_text(data.get("profile"))
			var base_text := last_profile_text
			if base_text == "" and data.has("profile"):
				base_text = _format_profile_text(data.get("profile"))
				last_profile_text = base_text
			if base_text == "":
				base_text = result_label.text
			var combined := base_text.strip_edges()
			if combined != "":
				combined += "\n\nИИ анализ:\n" + analysis_text
			else:
				combined = "ИИ анализ:\n" + analysis_text
			result_label.text = combined
			if analysis_button:
				analysis_button.disabled = false
			return
		last_profile_text = _format_profile_text(data)
		result_label.text = last_profile_text
		if analysis_button:
			analysis_button.disabled = false
	else:
		result_label.text = "Ошибка %d: %s" % [code, text]
		if analysis_button and last_profile_text != "":
			analysis_button.disabled = false
# Создаём блок кнопок под результатом, включая запуск AI-анализa
func _create_actions_box() -> void:
	actions_box = HBoxContainer.new()
	actions_box.name = "ResultActions"
	add_child(actions_box)

	# позиционируем под result_label (простая раскладка с абсолютными оффсетами сцены)
	actions_box.anchor_left = 0
	actions_box.anchor_right = 0
	actions_box.anchor_top = 0
	actions_box.anchor_bottom = 0
	actions_box.offset_left = result_label.offset_left
	actions_box.offset_top = result_label.offset_bottom + 16
	actions_box.offset_right = result_label.offset_right
	actions_box.offset_bottom = actions_box.offset_top + 40
	actions_box.visible = true

	var b1 := Button.new(); b1.text = "Совместимость"
	var b2 := Button.new(); b2.text = "Годы"
	var b3 := Button.new(); b3.text = "Месяцы"
	var b4 := Button.new(); b4.text = "Детали"

	b1.pressed.connect(func(): _on_extra("compat"))
	b2.pressed.connect(func(): _on_extra("years"))
	b3.pressed.connect(func(): _on_extra("months"))
	b4.pressed.connect(func(): _on_extra("details"))

	analysis_button = Button.new()
	analysis_button.text = "ИИ-анализ профиля"
	analysis_button.disabled = true
	analysis_button.pressed.connect(_on_analysis_pressed)
	actions_box.add_child(analysis_button)

	actions_box.add_child(b1)
	actions_box.add_child(b2)
	actions_box.add_child(b3)
	actions_box.add_child(b4)


# Обработчик кнопки AI: если профиль загружен, запускаем второй запрос
func _on_analysis_pressed() -> void:
	if last_profile_text == "":
		return
	_send_analysis_request()
func _on_extra(kind: String) -> void:
	match kind:
		"compat":
			# TODO: вызвать свой эндпоинт совместимости или локальный расчёт
			result_label.text += "\n→ Совместимость: скоро"
		"years":
			result_label.text += "\n→ Годы: скоро"
		"months":
			result_label.text += "\n→ Месяцы: скоро"
		"details":
			result_label.text += "\n→ Детали: скоро"


# Форматируем словарь профиля в многострочный текст для ResultLabel
func _format_profile_text(profile: Dictionary) -> String:
	return "Путь жизни: %s\nЧисло рождения: %s\nВыражение: %s\nДуша: %s\nЛичность: %s" % [
		str(profile.get("life_path", "")),
		str(profile.get("birthday", "")),
		str(profile.get("expression", "")),
		str(profile.get("soul", "")),
		str(profile.get("personality", ""))
	]
