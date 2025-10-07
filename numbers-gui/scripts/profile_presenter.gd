extends RefCounted
class_name ProfilePresenter

const ANALYSIS_HEADING := "AI анализ:"
const ANALYSIS_FALLBACK := "Анализ временно недоступен."


func format_profile(profile: Dictionary) -> String:
	var lines := [
		"Число жизненного пути: %s" % str(profile.get("life_path", "")),
		"Число дня рождения: %s" % str(profile.get("birthday", "")),
		"Число выражения: %s" % str(profile.get("expression", "")),
		"Число души: %s" % str(profile.get("soul", "")),
		"Число личности: %s" % str(profile.get("personality", "")),
	]
	return "\n".join(lines)


func combine_with_analysis(profile_text: String, analysis_text: String) -> String:
	var base := profile_text.strip_edges()
	var analysis := analysis_text.strip_edges()
	if analysis == "":
		analysis = ANALYSIS_FALLBACK

	if base != "":
		return "%s\n\n%s\n%s" % [base, ANALYSIS_HEADING, analysis]
	return "%s\n%s" % [ANALYSIS_HEADING, analysis]

