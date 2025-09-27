extends Control

# Получаем ссылки на элементы интерфейса
@onready var date_input: LineEdit = $DateLineEdit
@onready var name_input: LineEdit = $NameLineEdit
@onready var date_button: Button = $DateButton
@onready var name_button: Button = $NameButton
@onready var date_label = $DateLabel
@onready var name_label = $NameLabel

func _ready() -> void:
    # Подписываем кнопки на обработчики
    date_button.pressed.connect(_on_date_button_pressed)
    name_button.pressed.connect(_on_name_button_pressed)

func _on_date_button_pressed() -> void:
    # Показываем введенную дату
    date_label.text = "Дата: " + date_input.text

func _on_name_button_pressed() -> void:
    # Показываем введённое ФИО
    name_label.text = "ФИО: " + name_input.text
