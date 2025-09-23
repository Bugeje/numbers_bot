extends Control  # Скрипт на корневом узле сцены.

# --- Ссылки на ноды ---
@onready var btn: Button = $Button

# --- Диалог ввода создадим программно, чтобы в сцене оставалась только 1 кнопка ---
var dlg: AcceptDialog
var input: LineEdit

func _ready() -> void:
	# Создаём диалог и поле ввода на лету (они невидимы до вызова popup).
	dlg = AcceptDialog.new()
	dlg.title = "Введите текст"
	dlg.ok_button_text = "Готово"
	add_child(dlg)

	input = LineEdit.new()
	input.placeholder_text = "Ваш текст"
	input.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	dlg.add_child(input)

	# Нажатие на кнопку — открыть диалог, очистив предыдущее значение.
	btn.pressed.connect(func():
		input.text = ""
		dlg.popup_centered()  # Показать диалог по центру экрана.
		input.grab_focus()
	)

	# Подтверждение диалога — переносим введённый текст на кнопку (если не пусто).
	dlg.confirmed.connect(func():
		var t := input.text.strip_edges()
		if t != "":
			btn.text = t
	)
