extends Control

# Получаем ссылки на элементы интерфейса
@onready var date_input: LineEdit = $DateLineEdit
@onready var name_input: LineEdit = $NameLineEdit
@onready var date_button: Button = $DateButton
@onready var name_button: Button = $NameButton
@onready var date_label: Label = $DateLabel
@onready var name_label: Label = $NameLabel

var date_regex := RegEx.new()
var name_regex := RegEx.new()

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
	var parts := text.split(" ", false)
	if parts.size() < 2:
		name_label.text = "Ошибка: нужно минимум Имя и Фамилия"
		return
	for part in parts:
		if name_regex.search(part) == null:
			name_label.text = "Ошибка: допустимы только буквы"
			return
	name_label.text = "ФИО корректно: " + text
