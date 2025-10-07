extends Control

const ProfileService = preload("res://scripts/profile_service.gd")
const InputFlow = preload("res://scripts/input_flow.gd")
const ProfilePresenter = preload("res://scripts/profile_presenter.gd")
const ExtrasController = preload("res://scripts/extras_controller.gd")

## Привязки к узлам сцены.

@onready var date_input: LineEdit = $DateLineEdit
@onready var name_input: LineEdit = $NameLineEdit
@onready var date_button: Button = $DateButton
@onready var name_button: Button = $NameButton
@onready var profile_button: Button = $ProfileButton
@onready var date_label: Label = $DateLabel
@onready var name_label: Label = $NameLabel
@onready var result_label: Label = $ResultLabel
@onready var http: HTTPRequest = $HTTPRequest

## Экземпляры вспомогательных классов для проверки ввода, форматирования и подсказок.
var flow := InputFlow.new()
var presenter := ProfilePresenter.new()
var extras := ExtrasController.new()
var service: ProfileService

var actions_box: HBoxContainer
var analysis_button: Button
var last_profile_text := ""
var current_step := InputFlow.Step.NAME


func _ready() -> void:
	## Инициализируем вспомогательные классы, подписываемся на сигналы и показываем первый шаг.
	service = ProfileService.new()
	add_child(service)
	service.setup(http)
	service.request_started.connect(_on_request_started)
	service.request_finished.connect(_on_request_finished)
	service.profile_ready.connect(_on_profile_ready)
	service.analysis_ready.connect(_on_analysis_ready)
	service.request_failed.connect(_on_request_failed)

	name_button.pressed.connect(_on_name_confirm)
	date_button.pressed.connect(_on_date_confirm)

	profile_button.visible = false
	_show_step(InputFlow.Step.NAME)


func _show_step(step: InputFlow.Step) -> void:
	## Показываем нужный блок ввода в зависимости от текущего шага мастера.
	current_step = step

	var show_name := step == InputFlow.Step.NAME
	var show_date := step == InputFlow.Step.DATE
	var show_result := step == InputFlow.Step.RESULT

	name_input.visible = show_name
	name_button.visible = show_name
	name_label.visible = show_name

	date_input.visible = show_date
	date_button.visible = show_date
	date_label.visible = show_date

	result_label.visible = show_result
	if show_result and actions_box == null:
		_create_actions_box()


func _on_name_confirm() -> void:
	## Валидируем ФИО, сохраняем и переходим к вводу даты.
	var outcome := flow.submit_name(name_input.text)
	name_label.text = outcome.get("message", "")
	if not outcome.get("ok", false):
		return

	name_input.text = outcome.get("value", name_input.text.strip_edges())
	_show_step(InputFlow.Step.DATE)


func _on_date_confirm() -> void:
	## Валидируем дату рождения и стартуем загрузку профиля.
	var outcome := flow.submit_birthdate(date_input.text)
	date_label.text = outcome.get("message", "")
	if not outcome.get("ok", false):
		return

	date_input.text = outcome.get("value", date_input.text.strip_edges())
	_show_step(InputFlow.Step.RESULT)
	_request_profile()


func _request_profile() -> void:
	## Делегируем API‑вызов на сервис и сбрасываем текст профиля.
	var payload := flow.get_payload()
	last_profile_text = ""
	service.request_profile(payload.get("full_name", ""), payload.get("birthdate", ""))


func _request_analysis() -> void:
	## Запускаем загрузку AI‑анализа для уже построенного профиля.
	var payload := flow.get_payload()
	service.request_analysis(payload.get("full_name", ""), payload.get("birthdate", ""))


func _on_request_started(kind: String) -> void:
	## Обновляем UI, когда начинается запрос, и блокируем кнопку анализа.
	if analysis_button:
		analysis_button.disabled = true
	if kind == "analysis":
		if last_profile_text != "":
			result_label.text = "%s\n\nAI анализ:\nЗагружаем анализ..." % last_profile_text
		else:
			result_label.text = "Загружаем анализ..."
	else:
		result_label.text = "Загружаем профиль..."


func _on_request_finished(_kind: String) -> void:
	## Сигнал завершения не требует действий, но оставлен для расширений.
	pass


func _on_profile_ready(profile: Dictionary) -> void:
	## Получили профиль — выводим и активируем кнопку AI.
	last_profile_text = presenter.format_profile(profile)
	result_label.text = last_profile_text
	if analysis_button:
		analysis_button.disabled = false


func _on_analysis_ready(profile: Dictionary, analysis: String) -> void:
	## Получили результат анализа — комбинируем текст и показываем пользователю.
	if profile.size() > 0:
		last_profile_text = presenter.format_profile(profile)
	result_label.text = presenter.combine_with_analysis(last_profile_text, analysis)
	if analysis_button:
		analysis_button.disabled = false


func _on_request_failed(kind: String, message: String) -> void:
	## Выводим человекочитаемое сообщение об ошибке и возвращаем UI в безопасное состояние.
	if kind == "analysis" and last_profile_text != "":
		result_label.text = "%s\n\nОшибка: %s" % [last_profile_text, message]
	else:
		result_label.text = "Ошибка: %s" % message
	if analysis_button and last_profile_text != "":
		analysis_button.disabled = false


func _create_actions_box() -> void:
	## Создаём контейнер с кнопками результата: AI и доп. опции.
	actions_box = HBoxContainer.new()
	actions_box.name = "ResultActions"
	add_child(actions_box)

	actions_box.anchor_left = 0
	actions_box.anchor_right = 0
	actions_box.anchor_top = 0
	actions_box.anchor_bottom = 0
	actions_box.offset_left = result_label.offset_left
	actions_box.offset_top = result_label.offset_bottom + 16
	actions_box.offset_right = result_label.offset_right
	actions_box.offset_bottom = actions_box.offset_top + 40
	actions_box.visible = true

	analysis_button = Button.new()
	analysis_button.text = "AI анализ"
	analysis_button.disabled = true
	analysis_button.pressed.connect(_on_analysis_pressed)
	actions_box.add_child(analysis_button)

	var buttons := {
		"compat": "Совместимость",
		"years": "Личные годы",
		"months": "Личные месяцы",
		"details": "Детали профиля",
	}

	for kind in buttons.keys():
		var btn := Button.new()
		btn.text = buttons[kind]
		btn.pressed.connect(func(): _on_extra(kind))
		actions_box.add_child(btn)


func _on_analysis_pressed() -> void:
	## Пользователь просит AI‑анализ — запускаем запрос, если есть базовый профиль.
	if last_profile_text == "":
		return
	_request_analysis()


func _on_extra(kind: String) -> void:
	## Добавляем текст‑подсказку для дополнительных опций (пока заглушки).
	var hint := extras.hint_for(kind)
	if hint == "":
		return

	if result_label.text.strip_edges() != "":
		result_label.text += "\n" + hint
	else:
		result_label.text = hint
