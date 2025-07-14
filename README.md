# PwnForum
## 🌐 OWASP Top-10 showcase проект

Данное приложение было разработано для демонстрации наиболее распространенных ошибок в безопасной веб-разработке, а также с целью показать некоторые способы их устранения.
Проект создан на Python с использованием `Flask` и `SQLite`.
Каждый пункт реализован в двух варинтах:
 - `vuln` — уязвимая версия
 - `fix` — возможный вариант исправления

## 🔧 Реализованные уязвимости
### 1. SQL-инъекция
Данный тип инъекции, как и почти все остальные, показывает разрыв между ожиданиями разработчика при проектировании приложения и реальным контекстом.
Конкретно в нашем примере, разработчик ожидает, что пользователь введет в поля логина и пароля свои данные для входа. На практике, пользователь может вводить в поля что угодно.
Так, например, в данной реализации поиска записи в БД:
```python
query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
result = c.execute(query).fetchone()
```
пользователь может ввести SQL запрос вместо своего пароля. Например: `' OR '1'='1`. Тогда запрос будет выглядеть следующим образом:
```sql
SELECT * FROM users WHERE username = 'admin' AND password = '' OR '1'='1'
```
Т.к. данное равенство всегда верно, приложение предоставит пользователю доступ как администратору.

---

Решение проблемы — ограничить пользователя вводом только тех данных, которые нас интресуют (логин и пароль). Сделать это можно так:
```python
query = "SELECT * FROM users WHERE username = ? AND password = ?"
result = c.execute(query, [username, password]).fetchone()
```
Данный синтаксис предотвратит попытки использовать SQL запорсы со стороны пользователя.
### 2. Plaintext Passwords
Хранить пароли в том же виде, в котором их вводит пользователь — плохая практика. При утечке базы данных, злоумышленник получит доступ ко всем аккаунтам без двухэтапной аутентификации. Более того, т.к. пользователи зачастую используют одинаковый (или схожий) пароль на разных сайтах, злоумышленник может попытаться получить доступ к другим аккаунтам пользователя. Решение проблемы — хэшировать пароль:
```python
hashed_password = generate_password_hash(password)
if db.add_user(username, hashed_password):
    session["username"] = username
    return redirect("/forum")
else:
    stored_password = db.get_user_password(username)
    if check_password_hash(stored_password, password):
        session["username"] = username
        return redirect("/forum")
    else:
        error_message = "Invalid credentials"
```
Тогда после утечки данных злоумышленник увидит такой пароль:
```sql
sqlite> SELECT password from users WHERE username='inno';
scrypt:32768:8:1$1nQYxR55zJbsPMz3$c1a5ac37dbefe3acac8965c331beb99c6bc68531caab0ef53bf69f2b1b00c04c1b487c4845242233a9a6e412c39094519950783d123ade51f22164b67d7c4778
```
### 3. Аутентификация
Аутентификация — важный аспект безопасной веб-разработки; перед тем, как мы предоставим пользователю доступ к какому-то ресурсу или функционалу, мы должны убедится, что этот пользователь — действительно тот, за кого он себя выдает.
Есть разные варианты сделать это. Например, после успешной авторизации, создать спецальный параметр в cookie:
```python
if result and username and password:
      resp = make_response(redirect("/forum"))
      resp.set_cookie("username", username)
      return resp
```
Далее на главной странице:
```python
username = request.cookies.get("username")
```
Вариант не самый удачный, т.к. немного понимающие пользователи могут создавать запросы со своими параметрами или cookies:
```html
curl -b "username=admin" http://127.0.0.1:5000/forum

    <!DOCTYPE html>
    <html>
    <head><title>Forum (Vulnerable)</title></head>
    <body>
    <h2>Welcome, admin</h2>
```
Никакого пароля, просто отдельный параметр в cookies. Аутентификация провалилась, атакующий успешно выдал себя за администратора.
Решение проблемы может быть следующим:
```python
if check_password_hash(stored_password, password):
    session["username"] = username
    return redirect("/forum")
```
Далее на главной странице:
```python
username = session.get("username")
if not username or not db.is_user_exists(username):
    return redirect("/")
```
Библиотека Flask предоставляет нам решение — сессии. Хранятся в cookie, подписаны секретным ключом.
В cookies это может выглядеть так: `session=eyJ1c2VybmFtZSI6ImFkbWluIn0.aG_d6Q.7WvVYUy6-1f4gytlTz3DRD9uWmc`.
Без этой сессии невозможно пройти аутентификацию, при этом получить нужное значение можно только зная секретный ключ.
### 4. Cross-Site Scripting (XSS)
Еще один пример непонимания разработчиком того контекста, с которым он работает. В нашем примере у пользователя форума есть возможность что-то запостить.
Уязвимость XSS возникает, когда разрабтчик упускает из виду, что пользователь может писать что угодно, например, код JavaScript.
Пример плохой реализации приложения:
```python
for post_user, content, timestamp, file_path in posts:
    html += f"""
    <div style='margin-bottom: 1em;'>
        <b>{post_user}</b> at {timestamp}<br>
        {content}<br>
        {f'<img src="{os.path.join(UPLOAD_FOLDER, file_path)}" style="max-width: 300px;">' if file_path else ""}
    </div>
    """
html += "</body></html>"
```
Данный подход (ручная генерация HTML) позволяет пользователю ввести в поле для публикации свой код:
```js
<script>alert(1)</script>
```
И этот код будет срабатывать при каждом открытии страницы.
Один из способов исправить это — использование шаблонов:
```html
{% for post in posts %}
<div style='margin-bottom: 1em;'>
    <b>{{ post[0] | e }}</b> at {{ post[2] | e }}<br>
    {{ post[1] | e }}<br>
    {% if post[3] %}
        <img src="{{ url_for('static', filename='uploads/' + post[3]) }}" 
              style="max-width: 300px; margin-top: 10px;">
    {% endif %}
</div>
{% endfor %}
```
Далее в коде:
```python
return render_template(
    "forum.html",
    posts=posts,
    username=username,
    static_files_path=url_for("static", filename=""),
)
```
Такой подход позволяет избежать исполнения кода, а весь пользовательский ввод будет воспринят как обычный текст.
### 5. Local File Inclusion (LFI)
Когда сервер предоставляет возможность просматривать какие-то внутренние файлы, пользователь может попробовать воспользоваться уязвимостью path traversal и получить доступ к файлам вне директории приложения.
В нашем примере пользователь может смотреть файлы со списком изменений веб-приложения:
```python
file_path = request.args.get("file", "")
try:
    with open(f"app/changelogs/{file_path}", "r") as f:
        content = f.read()
except Exception as e:
        content = f"Error reading file: {str(e)}"
```
Но ничто не мешает пользователю ввести такой путь:
`../../../../etc/passwd` и получить несанкционированный доступ к какой-то информации.
Решение проблемы — ограничение действий пользователя:
```python
from werkzeug.utils import secure_filename

user_arg = request.args.get("file", "")
file_path = secure_filename(user_arg)
try:
    with open(f"app/changelogs/{file_path}", "r") as f:
        content = f.read()
except Exception:
    content = "Incorrect input"
```
Здесь мы отбрасываем все спец. символы, более надежный вариант: создание "белого списка" файлов, к которым можно обратиться.
### 6. IDOR
Insecure Direct Object Reference — вид уязвимости, при котором доступ к ресурсу можно получить путем манипулирования URL строкой. Например, в этом веб-приложении пользователи могут создать заметку перед публикацией:
```python
@drafts_bp.route("/drafts/<username>", methods=["GET", "POST"])
def drafts(username):
     # ---
    drafts_for_user = db.get_user_drafts(username)
    drafts_for_user.reverse()
     # ---
    for draft in drafts_for_user:
        html += f"""
        <div style='margin-bottom: 1em;'>
        Draft ID: {draft[0]}<br>
        {draft[2]}<br>
        {f'<a href="{draft[3]}">File</a>' if draft[3] else ""}
        </div>
        """
```
Таким образом, любой может подставить чужой юзернейм и получить доступ к чужим заметкам. Например, для просмотра заметок администратора, достаточно заменить в URL `drafts/inno` на `drafts/admin`.
Решений может быть несколько:
- надежная авторизация:
```python
session_user = session.get("username")
if username != sesion_user:
    abort (403, "Forbidden")
```
- скрыть параметр в ссылке:
```python
@drafts_bp.route("/drafts", methods=["GET", "POST"])
def drafts():
    username = session["username"]
    if not username or not db.is_user_exists(username):
        return redirect("/")
```
### 7. Unrestricted File Upload
Данная уязвимость возникает когда разработчик не смог правильно ограничить загружаемые пользователем файлы. Иногда на первый взгляд кажется, что в коде есть грамотная проверка файла:
```python
def is_allowed(filename):
    allowed_extensions = {"png", "jpg", "jpeg"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions
# ---
if file and file.filename and is_allowed(file.filename):
    file_path = os.path.join("app", UPLOAD_FOLDER, file.filename)
    file.save(file_path)
```
Казалось бы, здесь мы грамотно разбиваем название файла по символу `.`, используем `rsplit()` и только один раз,
то есть файлы вроде malware.png.py и т.п. не прокатят. На самом же деле, ничто не мешает отправить такой запрос:
```bash
curl -X POST \
  -F "draft_content=Malicious draft" \
  -F "file=@malicious.py;filename=image.png" \
  -F "action=save" \
  http://127.0.0.1:5000/drafts/inno
```
Или же просто записать содержимое вредоноса в `.png`. Более того, в этой уязвимой версии мы можем загрузить
файлы вне заданной директории с помощью префикса `../`:
```bash
curl -X POST \
  -F "draft_content=Malicious draft" \
  -F "file=@malicious.py;filename=../image.png" \
  -F "action=save" \
  http://127.0.0.1:5000/drafts/inno
```
С таким подходом можно, например, переписать файлы самого приложения.

---

Фикс — тщательная проверка загружаемых файлов перед их сохранением:
```python
def is_safe_file(file):
    filename = secure_filename(file.filename) # Path traversal fix
    if not filename:
        return False

    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False

    try:
        img = Image.open(file)
        img.verify()  # Verifies that it is, indeed, an image
    except Exception:
        return False
    file.seek(0)

    return True
```
Еще одна небольшая доработка: создание уникальных имён для файлов:
```python
def generate_filename(filename) -> str:
    safe_name = secure_filename(filename)
    prefix = uuid.uuid4().hex[:10]
    if not safe_name:
        return prefix
    return f"{prefix}_{safe_name}"
```

---

## 📦 Установка и запуск
Для запуска и тестирования в локальной среде:
```bash
git clone https://github.com/inno1314/PwnForum.git

python3 -m venv .venv
source .venv/bin/activate

pip3 install -r requirements.txt
echo "APP_MODE=vuln" >> .env
flask run
```
Заменить `APP_MODE=fix` для запуска исправленной версии сайта.
