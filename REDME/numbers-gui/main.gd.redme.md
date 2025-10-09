# Разбор `main.gd`

| Код | Комментарий |
| --- | --- |
| <code>extends Control</code> | <span style="color:green"># главный скрипт сцены: наследуемся от Control</span> |
| <code></code> | <span style="color:green"></span> |
| <code>const ProfileService = preload("res://scripts/profile_service.gd")</code> | <span style="color:green"># заранее загружаем сервис запросов</span> |
| <code>const InputFlow = preload("res://scripts/input_flow.gd")</code> | <span style="color:green"># загружаем менеджер шагов ввода</span> |
| <code>const ProfilePresenter = preload("res://scripts/profile_presenter.gd")</code> | <span style="color:green"># класс для форматирования результата</span> |
| <code>const ExtrasController = preload("res://scripts/extras_controller.gd")</code> | <span style="color:green"># контроллер подсказок для дополнительных кнопок</span> |
| <code></code> | <span style="color:green"></span> |
| <code>## Здесь перечислены узлы сцены, к которым нужен быстрый доступ.</code> | <span style="color:green"># комментарий из исходника</span> |
| <code>@onready var date_input: LineEdit = $DateLineEdit</code> | <span style="color:green"># поле ввода даты рождения</span> |
| <code>@onready var name_input: LineEdit = $NameLineEdit</code> | <span style="color:green"># поле ввода имени</span> |
| <code>@onready var date_button: Button = $DateButton</code> | <span style="color:green"># кнопка подтверждения даты</span> |
| <code>@onready var name_button: Button = $NameButton</code> | <span style="color:green"># кнопка подтверждения имени</span> |
| <code>@onready var profile_button: Button = $ProfileButton</code> | <span style="color:green"># кнопка «получить профиль» (пока скрыта)</span> |
| <code>@onready var date_label: Label = $DateLabel</code> | <span style="color:green"># подпись/ошибка для даты</span> |
| <code>@onready var name_label: Label = $NameLabel</code> | <span style="color:green"># подпись/ошибка для имени</span> |
| <code>@onready var result_label: Label = $ResultLabel</code> | <span style="color:green"># область вывода результата</span> |
| <code>@onready var http: HTTPRequest = $HTTPRequest</code> | <span style="color:green"># узел HTTPRequest для сетевых запросов</span> |
| <code></code> | <span style="color:green"></span> |
| <code>## Создаём помощников: проверка ввода, форматирование, подсказки и сервис.</code> | <span style="color:green"># комментарий из исходника</span> |
| <code>var flow := InputFlow.new()</code> | <span style="color:green"># менеджер шагов ввода</span> |
| <code>var presenter := ProfilePresenter.new()</code> | <span style="color:green"># форматирование текста профиля</span> |
| <code>var extras := ExtrasController.new()</code> | <span style="color:green"># подсказки для дополнительных кнопок</span> |
| <code>var service: ProfileService</code> | <span style="color:green"># сервис сетевых запросов (инициализируем позже)</span> |
| <code></code> | <span style="color:green"></span> |
| <code>var actions_box: HBoxContainer</code> | <span style="color:green"># контейнер с дополнительными кнопками результата</span> |
| <code>var analysis_button: Button</code> | <span style="color:green"># кнопка вызова AI-анализа</span> |
| <code>var last_profile_text := ""</code> | <span style="color:green"># здесь хранится последний текст профиля</span> |
| <code>var current_step := InputFlow.Step.NAME</code> | <span style="color:green"># текущий шаг мастера ввода</span> |
| <code></code> | <span style="color:green"></span> |
| <code>func _ready() -> void:</code> | <span style="color:green"># точка входа: настраиваем всё при запуске сцены</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;service = ProfileService.new()</code> | <span style="color:green"># создаём экземпляр сервиса</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;add_child(service)</code> | <span style="color:green"># добавляем его в дерево, чтобы он работал как узел</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;service.setup(http)</code> | <span style="color:green"># передаём внутрь HTTPRequest</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;service.request_started.connect(_on_request_started)</code> | <span style="color:green"># подписываемся на сигнал «запрос начат»</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;service.request_finished.connect(_on_request_finished)</code> | <span style="color:green"># сигнал «запрос завершён»</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;service.profile_ready.connect(_on_profile_ready)</code> | <span style="color:green"># сигнал с готовым профилем</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;service.analysis_ready.connect(_on_analysis_ready)</code> | <span style="color:green"># сигнал с анализом</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;service.request_failed.connect(_on_request_failed)</code> | <span style="color:green"># сигнал об ошибке</span> |
| <code></code> | <span style="color:green"></span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;name_button.pressed.connect(_on_name_confirm)</code> | <span style="color:green"># обрабатываем нажатие на кнопку имени</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;date_button.pressed.connect(_on_date_confirm)</code> | <span style="color:green"># обрабатываем ввод даты</span> |
| <code></code> | <span style="color:green"></span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;profile_button.visible = false</code> | <span style="color:green"># кнопка профиля скрыта (используется другой поток)</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;_show_step(InputFlow.Step.NAME)</code> | <span style="color:green"># показываем пользователю первый шаг — ввод имени</span> |
| <code></code> | <span style="color:green"></span> |
| <code>func _show_step(step: InputFlow.Step) -> void:</code> | <span style="color:green"># переключаем видимость элементов под нужный этап</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;current_step = step</code> | <span style="color:green"># запоминаем новый шаг</span> |
| <code></code> | <span style="color:green"></span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;var show_name := step == InputFlow.Step.NAME</code> | <span style="color:green"># нужно ли показывать блок имени</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;var show_date := step == InputFlow.Step.DATE</code> | <span style="color:green"># блок даты</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;var show_result := step == InputFlow.Step.RESULT</code> | <span style="color:green"># блок результата</span> |
| <code></code> | <span style="color:green"></span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;name_input.visible = show_name</code> | <span style="color:green"># показываем/прячем поле имени</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;name_button.visible = show_name</code> | <span style="color:green"># кнопка подтверждения имени</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;name_label.visible = show_name</code> | <span style="color:green"># подсказка под именем</span> |
| <code></code> | <span style="color:green"></span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;date_input.visible = show_date</code> | <span style="color:green"># поле даты</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;date_button.visible = show_date</code> | <span style="color:green"># кнопка даты</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;date_label.visible = show_date</code> | <span style="color:green"># подсказка для даты</span> |
| <code></code> | <span style="color:green"></span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;result_label.visible = show_result</code> | <span style="color:green"># видимость блока результата</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;if show_result and actions_box == null:</code> | <span style="color:green"># если впервые показываем результат, создаём кнопки</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_create_actions_box()</code> | <span style="color:green"># создаём контейнер действий</span> |
| <code></code> | <span style="color:green"></span> |
| <code>func _on_name_confirm() -> void:</code> | <span style="color:green"># обработчик подтверждения имени</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;var outcome := flow.submit_name(name_input.text)</code> | <span style="color:green"># передаём введённый текст в InputFlow</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;name_label.text = outcome.get("message", "")</code> | <span style="color:green"># показываем подсказку или успех</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;if not outcome.get("ok", false):</code> | <span style="color:green"># если проверка не прошла — выходим</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | <span style="color:green"># ждём исправлений</span> |
| <code></code> | <span style="color:green"></span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;name_input.text = outcome.get("value", name_input.text.strip_edges())</code> | <span style="color:green"># заменяем текст на нормализованное значение</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;_show_step(InputFlow.Step.DATE)</code> | <span style="color:green"># переходим к шагу с датой</span> |
| <code></code> | <span style="color:green"></span> |
| <code>func _on_date_confirm() -> void:</code> | <span style="color:green"># обработчик подтверждения даты</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;var outcome := flow.submit_birthdate(date_input.text)</code> | <span style="color:green"># проверяем дату через InputFlow</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;date_label.text = outcome.get("message", "")</code> | <span style="color:green"># показываем подсказку</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;if not outcome.get("ok", false):</code> | <span style="color:green"># при ошибке останавливаемся</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | <span style="color:green"># ждём исправлений</span> |
| <code></code> | <span style="color:green"></span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;date_input.text = outcome.get("value", date_input.text.strip_edges())</code> | <span style="color:green"># заменяем на нормализованную дату</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;_show_step(InputFlow.Step.RESULT)</code> | <span style="color:green"># показываем экран с результатом</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;_request_profile()</code> | <span style="color:green"># сразу запускаем расчёт профиля</span> |
| <code></code> | <span style="color:green"></span> |
| <code>func _request_profile() -> void:</code> | <span style="color:green"># обёртка для вызова сервиса профиля</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;var payload := flow.get_payload()</code> | <span style="color:green"># получаем имя и дату из InputFlow</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;last_profile_text = ""</code> | <span style="color:green"># очищаем предыдущий текст профиля</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;service.request_profile(payload.get("full_name", ""), payload.get("birthdate", ""))</code> | <span style="color:green"># отправляем запрос в API</span> |
| <code></code> | <span style="color:green"></span> |
| <code>func _request_analysis() -> void:</code> | <span style="color:green"># обёртка для запроса анализа</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;var payload := flow.get_payload()</code> | <span style="color:green"># снова получаем имя и дату</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;service.request_analysis(payload.get("full_name", ""), payload.get("birthdate", ""))</code> | <span style="color:green"># запрашиваем анализ</span> |
| <code></code> | <span style="color:green"></span> |
| <code>func _on_request_started(kind: String) -> void:</code> | <span style="color:green"># реагируем на старт запроса</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;if analysis_button:</code> | <span style="color:green"># если кнопка анализа существует</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;analysis_button.disabled = true</code> | <span style="color:green"># блокируем её до окончания запроса</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;if kind == "analysis":</code> | <span style="color:green"># меняем текст для запроса анализа</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if last_profile_text != "":</code> | <span style="color:green"># если профиль уже показан</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;result_label.text = "%s\n\nAI анализ:\nЗагружаем анализ..." % last_profile_text</code> | <span style="color:green"># добавляем строку о загрузке анализа</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;else:</code> | <span style="color:green"># если профиля ещё нет</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;result_label.text = "Загружаем анализ..."</code> | <span style="color:green"># выводим сообщение</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;else:</code> | <span style="color:green"># обработка запроса профиля</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;result_label.text = "Загружаем профиль..."</code> | <span style="color:green"># выводим сообщение о загрузке профиля</span> |
| <code></code> | <span style="color:green"></span> |
| <code>func _on_request_finished(_kind: String) -> void:</code> | <span style="color:green"># обработчик завершения запроса (пока ничего не делает)</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;pass</code> | <span style="color:green"># оставлено на будущее</span> |
| <code></code> | <span style="color:green"></span> |
| <code>func _on_profile_ready(profile: Dictionary) -> void:</code> | <span style="color:green"># получили профиль от сервиса</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;last_profile_text = presenter.format_profile(profile)</code> | <span style="color:green"># формируем текст профиля</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;result_label.text = last_profile_text</code> | <span style="color:green"># выводим его пользователю</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;if analysis_button:</code> | <span style="color:green"># если кнопка анализа уже создана</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;analysis_button.disabled = false</code> | <span style="color:green"># разрешаем запрашивать анализ</span> |
| <code></code> | <span style="color:green"></span> |
| <code>func _on_analysis_ready(profile: Dictionary, analysis: String) -> void:</code> | <span style="color:green"># получили результат анализа</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;if profile.size() > 0:</code> | <span style="color:green"># если сервер вернул обновлённый профиль</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;last_profile_text = presenter.format_profile(profile)</code> | <span style="color:green"># пересобираем текст профиля</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;result_label.text = presenter.combine_with_analysis(last_profile_text, analysis)</code> | <span style="color:green"># объединяем профиль и анализ</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;if analysis_button:</code> | <span style="color:green"># снова разблокируем кнопку анализа</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;analysis_button.disabled = false</code> | <span style="color:green"># теперь можно запускать повторно</span> |
| <code></code> | <span style="color:green"></span> |
| <code>func _on_request_failed(kind: String, message: String) -> void:</code> | <span style="color:green"># показываем сообщение об ошибке</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;if kind == "analysis" and last_profile_text != "":</code> | <span style="color:green"># если ошибка анализа и есть текст профиля</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;result_label.text = "%s\n\nОшибка: %s" % [last_profile_text, message]</code> | <span style="color:green"># добавляем ошибку под профиль</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;else:</code> | <span style="color:green"># иначе просто показываем ошибку</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;result_label.text = "Ошибка: %s" % message</code> | <span style="color:green"># выводим текст ошибки</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;if analysis_button and last_profile_text != "":</code> | <span style="color:green"># если есть кнопка и профиль был получен</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;analysis_button.disabled = false</code> | <span style="color:green"># снова разрешаем пробовать</span> |
| <code></code> | <span style="color:green"></span> |
| <code>func _create_actions_box() -> void:</code> | <span style="color:green"># создаём контейнер с кнопками для результата</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;actions_box = HBoxContainer.new()</code> | <span style="color:green"># создаём горизонтальный контейнер</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;actions_box.name = "ResultActions"</code> | <span style="color:green"># даём имя узлу</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;add_child(actions_box)</code> | <span style="color:green"># добавляем контейнер в сцену</span> |
| <code></code> | <span style="color:green"></span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;actions_box.anchor_left = 0</code> | <span style="color:green"># растягиваем контейнер по ширине</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;actions_box.anchor_right = 0</code> | <span style="color:green"># устанавливаем правый якорь</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;actions_box.anchor_top = 0</code> | <span style="color:green"># верхний якорь</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;actions_box.anchor_bottom = 0</code> | <span style="color:green"># нижний якорь</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;actions_box.offset_left = result_label.offset_left</code> | <span style="color:green"># выравниваем по левому краю result_label</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;actions_box.offset_top = result_label.offset_bottom + 16</code> | <span style="color:green"># размещаем ниже результата</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;actions_box.offset_right = result_label.offset_right</code> | <span style="color:green"># ширина совпадает с result_label</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;actions_box.offset_bottom = actions_box.offset_top + 40</code> | <span style="color:green"># задаём высоту контейнера</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;actions_box.visible = true</code> | <span style="color:green"># делаем контейнер видимым</span> |
| <code></code> | <span style="color:green"></span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;analysis_button = Button.new()</code> | <span style="color:green"># создаём кнопку AI-анализа</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;analysis_button.text = "AI анализ"</code> | <span style="color:green"># подпись на кнопке</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;analysis_button.disabled = true</code> | <span style="color:green"># по умолчанию заблокирована</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;analysis_button.pressed.connect(_on_analysis_pressed)</code> | <span style="color:green"># подключаем обработчик нажатия</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;actions_box.add_child(analysis_button)</code> | <span style="color:green"># добавляем кнопку в контейнер</span> |
| <code></code> | <span style="color:green"></span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;var buttons := {</code> | <span style="color:green"># словарь с подписями дополнительных кнопок</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"compat": "Совместимость",</code> | <span style="color:green"># кнопка совместимости</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"years": "Личные годы",</code> | <span style="color:green"># кнопка личных лет</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"months": "Личные месяцы",</code> | <span style="color:green"># кнопка личных месяцев</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"details": "Детали профиля",</code> | <span style="color:green"># кнопка деталей профиля</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;}</code> | <span style="color:green"># закрываем словарь</span> |
| <code></code> | <span style="color:green"></span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;for kind in buttons.keys():</code> | <span style="color:green"># создаём каждую дополнительную кнопку</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;var btn := Button.new()</code> | <span style="color:green"># новая кнопка</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;btn.text = buttons[kind]</code> | <span style="color:green"># подписываем её</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;btn.pressed.connect(func(): _on_extra(kind))</code> | <span style="color:green"># нажатие вызывает _on_extra с нужным ключом</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;actions_box.add_child(btn)</code> | <span style="color:green"># добавляем кнопку в контейнер</span> |
| <code></code> | <span style="color:green"></span> |
| <code>func _on_analysis_pressed() -> void:</code> | <span style="color:green"># пользователь попросил AI-анализ</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;if last_profile_text == "":</code> | <span style="color:green"># без текста профиля анализ не запускаем</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | <span style="color:green"># выходим</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;_request_analysis()</code> | <span style="color:green"># отправляем запрос анализа</span> |
| <code></code> | <span style="color:green"></span> |
| <code>func _on_extra(kind: String) -> void:</code> | <span style="color:green"># обработка дополнительных кнопок</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;var hint := extras.hint_for(kind)</code> | <span style="color:green"># получаем подсказку от ExtrasController</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;if hint == "":</code> | <span style="color:green"># если подсказки нет</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | <span style="color:green"># ничего не делаем</span> |
| <code></code> | <span style="color:green"></span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;if result_label.text.strip_edges() != "":</code> | <span style="color:green"># если в результате уже есть текст</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;result_label.text += "\n" + hint</code> | <span style="color:green"># добавляем подсказку новой строкой</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;else:</code> | <span style="color:green"># если поле пустое</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;result_label.text = hint</code> | <span style="color:green"># просто выводим подсказку</span> |

**Итог:** `main.gd` управляет всей сценой — переключает шаги ввода, вызывает сервис, отображает профиль, просит AI-анализ и показывает подсказки для дополнительных действий.
