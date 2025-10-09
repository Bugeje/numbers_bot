# Разбор `extras_controller.gd`

Ниже каждая строка кода снабжена пояснением. Цвет появляется в Markdown‑предпросмотре.

| Код | Комментарий |
| --- | --- |
| <code>extends RefCounted</code> | <span style="color:green"># создаём вспомогательный класс без привязки к узлу</span> |
| <code>class_name ExtrasController</code> | <span style="color:green"># регистрируем имя класса, чтобы к нему можно было обратиться из других скриптов</span> |
| <code>## Контроллер хранит тексты для дополнительных кнопок (совместимость/годы/месяцы).</code> | <span style="color:green"># строка описания файла, оставленная в исходнике</span> |
| <code>const HINTS := {</code> | <span style="color:green"># словарь с текстами подсказок по ключам</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;"compat": "Совместимость: расчёты появятся позже.",</code> | <span style="color:green"># подсказка для кнопки совместимости</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;"years": "Личные годы: модуль в разработке.",</code> | <span style="color:green"># подсказка для раздела «Личные годы»</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;"months": "Личные месяцы: модуль в разработке.",</code> | <span style="color:green"># подсказка для раздела «Личные месяцы»</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;"details": "Детальный профиль: функция готовится к запуску.",</code> | <span style="color:green"># текст для кнопки «Детали профиля»</span> |
| <code>}</code> | <span style="color:green"># закрываем словарь подсказок</span> |
| <code></code> | <span style="color:green"></span> |
| <code>func hint_for(kind: String) -> String:</code> | <span style="color:green"># метод получает ключ и возвращает подходящую подсказку</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;## Возвращаем текст по ключу или фразу по умолчанию.</code> | <span style="color:green"># комментарий из исходника: зачем нужен метод</span> |
| <code>&nbsp;&nbsp;&nbsp;&nbsp;return HINTS.get(kind, "Функция временно недоступна.")</code> | <span style="color:green"># достаём значение из словаря, если нет — выдаём заглушку</span> |

**Главная мысль:** контроллер хранит короткие сообщения для дополнительных кнопок, чтобы UI мог подсказать пользователю, что разделы пока в разработке.
