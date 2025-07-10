from flask import Blueprint, request, render_template_string, redirect, session

auth_bp = Blueprint("auth_fix", __name__)


@auth_bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        import sqlite3

        conn = sqlite3.connect("app/db.sqlite3")
        c = conn.cursor()
        query = "SELECT * FROM users WHERE username = ? AND password = ?"
        result = c.execute(query, [username, password]).fetchone()

        if result and username and password:
            session["username"] = username
            return redirect("/forum")
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
    session.clear()
    return redirect("/")
