from flask import (
    Blueprint,
    request,
    make_response,
    render_template_string,
    redirect,
)

auth_bp = Blueprint("auth_vuln", __name__)


@auth_bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        import sqlite3

        conn = sqlite3.connect("app/db.sqlite3")
        c = conn.cursor()
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        result = c.execute(query).fetchone()

        if result and username and password:
            resp = make_response(redirect("/forum"))
            resp.set_cookie("username", username)
            return resp
        else:
            return "Ошибка: неверные данные"

    return render_template_string("""
    <form method="POST">
        <input name="username" placeholder="Username">
        <input name="password" placeholder="Password">
        <button type="submit">Login</button>
    </form>
    """)


@auth_bp.route("/logout")
def logout():
    return redirect("/")
