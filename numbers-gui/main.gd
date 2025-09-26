extends Control

# Кэшируем ссылки на узлы интерфейса по именам из сцены
@onready var input_field: LineEdit = $LineEdit
@onready var result_label: Label = $Label
@onready var submit_button: Button = $Button

func _ready() -> void:
    # Привязываем сигнал нажатия к обработчику после готовности сцены
    submit_button.pressed.connect(_on_button_pressed)

func _on_button_pressed() -> void:
    # Берём текст из поля ввода и показываем его в Label
    var user_text := input_field.text
    result_label.text = "Result: " + user_text
