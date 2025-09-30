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

const PROFILE_ENDPOINT := "http://127.0.0.1:8001/profile" # замените на IP ПК

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
	if show_name:
		name_label.text = "Введите ФИО (минимум два слова)"

	# дата
	date_input.visible = show_date
	date_button.visible = show_date
	date_label.visible = show_date
	if show_date:
		date_label.text = "Введите дату рождения (ДД.ММ.ГГГГ)"

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
	_send_request()

func _send_request() -> void:
	if busy:
		return
	var payload := {
		"full_name": name_input.text.strip_edges(),
		"birthdate": date_input.text.strip_edges()
	}
	var headers := ["Content-Type: application/json"]
	var body := JSON.stringify(payload)
	busy = true
	result_label.text = "Считаю…"
	var err := http.request(PROFILE_ENDPOINT, headers, HTTPClient.METHOD_POST, body)
	if err != OK:
		busy = false
		result_label.text = "Ошибка отправки: %s" % str(err)

func _on_request_completed(result: int, code: int, _h: PackedStringArray, body: PackedByteArray) -> void:
	busy = false
	if result != HTTPRequest.RESULT_SUCCESS:
		result_label.text = "Ошибка сети: %d" % result
		return

	var text := body.get_string_from_utf8()
	var data: Variant = JSON.parse_string(text)
	if code == 200 and typeof(data) == TYPE_DICTIONARY:
		result_label.text = "Жизненный путь: %s\nДень рождения: %s\nВыражение: %s\nДуша: %s\nЛичность: %s" % [
			str(data.get("life_path", "")),
			str(data.get("birthday", "")),
			str(data.get("expression", "")),
			str(data.get("soul", "")),
			str(data.get("personality", ""))
		]
	else:
		result_label.text = "Ошибка %d: %s" % [code, text]

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

	actions_box.add_child(b1)
	actions_box.add_child(b2)
	actions_box.add_child(b3)
	actions_box.add_child(b4)

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
