extends RefCounted
class_name InputFlow

enum Step { NAME, DATE, RESULT }

const NAME_ERROR_SHORT := "Пожалуйста, укажите минимум имя и фамилию."
const NAME_ERROR_INVALID := "Имя может содержать только буквы, дефис и апостроф."
const NAME_OK := "Ок"
const DATE_ERROR := "Неверный формат. Используйте ДД.ММ.ГГГГ."
const DATE_OK := "Ок"

var _date_regex := RegEx.new()
var _name_part_regex := RegEx.new()

var current_step: Step = Step.NAME
var full_name := ""
var birthdate := ""


func _init() -> void:
	_date_regex.compile(r"^(0[1-9]|[12]\d|3[01])\.(0[1-9]|1[0-2])\.(19\d{2}|20\d{2})$")
	_name_part_regex.compile(r"^[\p{L}][\p{L}\-']+$")


func reset() -> void:
	current_step = Step.NAME
	full_name = ""
	birthdate = ""


func submit_name(raw: String) -> Dictionary:
	var sanitized := raw.strip_edges()
	var parts: PackedStringArray = sanitized.split(" ", false)
	if parts.size() < 2:
		return {
			"ok": false,
			"message": NAME_ERROR_SHORT,
		}
	for part in parts:
		if _name_part_regex.search(part) == null:
			return {
				"ok": false,
				"message": NAME_ERROR_INVALID,
			}

	full_name = " ".join(parts)
	current_step = Step.DATE
	return {
		"ok": true,
		"message": NAME_OK,
		"step": current_step,
		"value": full_name,
	}


func submit_birthdate(raw: String) -> Dictionary:
	var sanitized := raw.strip_edges()
	if _date_regex.search(sanitized) == null:
		return {
			"ok": false,
			"message": DATE_ERROR,
		}

	birthdate = sanitized
	current_step = Step.RESULT
	return {
		"ok": true,
		"message": DATE_OK,
		"step": current_step,
		"value": birthdate,
	}


func get_payload() -> Dictionary:
	return {
		"full_name": full_name,
		"birthdate": birthdate,
	}

