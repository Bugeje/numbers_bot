# Разбор `profile_presenter.gd`

| Код | Комментарий |
| --- | --- |
| <code>extends RefCounted</code> | <span style="color:green"># делаем отдельный вспомогательный класс без узла</span> |
| <code>class_name ProfilePresenter</code> | <span style="color:green"># регистрируем имя класса, чтобы переиспользовать его из других скриптов</span> |
| <code>## Класс отвечает за сборку читаемого текста профиля.</code> | <span style="color:green"># описание назначения прямо в исходнике</span> |
| <code>const ANALYSIS_HEADING := "AI анализ:"</code> | <span style="color:green"># заголовок для блока с текстом от AI</span> |
| <code>const ANALYSIS_FALLBACK := "Анализ временно недоступен."</code> | <span style="color:green"># сообщение, если AI не прислал заключение</span> |
| <code></code> | <span style="color:green"></span> |
| <code>func format_profile(profile: Dictionary) -> String:</code> | <span style="color:green"># превращаем словарь с числами в многострочный текст</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;## Собираем строки для каждого ключевого показателя профиля.</code> | <span style="color:green"># комментарий из исходника: поясняет работу функции</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;var lines := [</code> | <span style="color:green"># создаём массив строк</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"Число жизненного пути: %s" % str(profile.get("life_path", "")),</code> | <span style="color:green"># первая строка — жизненный путь</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"Число дня рождения: %s" % str(profile.get("birthday", "")),</code> | <span style="color:green"># вторая строка — число дня рождения</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"Число выражения: %s" % str(profile.get("expression", "")),</code> | <span style="color:green"># число выражения</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"Число души: %s" % str(profile.get("soul", "")),</code> | <span style="color:green"># число души</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"Число личности: %s" % str(profile.get("personality", "")),</code> | <span style="color:green"># число личности</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;]</code> | <span style="color:green"># закрываем список строк</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;return "\n".join(lines)</code> | <span style="color:green"># объединяем строки переходами на новую строку</span> |
| <code></code> | <span style="color:green"></span> |
| <code>func combine_with_analysis(profile_text: String, analysis_text: String) -> String:</code> | <span style="color:green"># добавляем к профилю текст AI, если он есть</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;## Комбинируем текст профиля и анализ, добавляя заголовок и fallback.</code> | <span style="color:green"># комментарий автора: что делает метод</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;var base := profile_text.strip_edges()</code> | <span style="color:green"># убираем лишние пробелы вокруг текста профиля</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;var analysis := analysis_text.strip_edges()</code> | <span style="color:green"># очищаем пробелы вокруг анализа</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;if analysis == "":</code> | <span style="color:green"># если анализ пустой</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;analysis = ANALYSIS_FALLBACK</code> | <span style="color:green"># подставляем сообщение по умолчанию</span> |
| <code></code> | <span style="color:green"></span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;if base != "":</code> | <span style="color:green"># если текст профиля не пустой</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return "%s\n\n%s\n%s" % [base, ANALYSIS_HEADING, analysis]</code> | <span style="color:green"># склеиваем профиль и анализ с заголовком</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;return "%s\n%s" % [ANALYSIS_HEADING, analysis]</code> | <span style="color:green"># если профиля нет, возвращаем только анализ</span> |

**Главная мысль:** `ProfilePresenter` отвечает за красивое представление данных — формирует текст из словаря профиля и аккуратно добавляет к нему итог от AI.
