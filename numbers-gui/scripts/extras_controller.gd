extends RefCounted
class_name ExtrasController

const HINTS := {
	"compat": "Совместимость: расчёты появятся позже.",
	"years": "Личный год: модуль в разработке.",
	"months": "Личный месяц: модуль в разработке.",
	"details": "Расширенный профиль: готовится к запуску.",
}


func hint_for(kind: String) -> String:
	return HINTS.get(kind, "Функция временно недоступна.")

