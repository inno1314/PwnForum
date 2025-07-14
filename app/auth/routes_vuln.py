from flask import (
    Blueprint,
    request,
    render_template_string,
    redirect,
    session,
    make_response,
)
import sqlite3

auth_bp = Blueprint("auth_vuln", __name__)


@auth_bp.route("/", methods=["GET", "POST"])
def login():
    error_message = ""

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            error_message = "Fill all fields"
        else:
            conn = sqlite3.connect("app/db.sqlite3")
            c = conn.cursor()
            query = f"INSERT INTO users (username, password) VALUES ('{username}', '{password}')"
            try:
                c.execute(query)
                conn.commit()
                conn.close()
                resp = make_response(redirect("/forum"))
                resp.set_cookie("username", username)
                return resp
            except sqlite3.IntegrityError:
                query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
                print(f"Executing query: {query}")
                result = c.execute(query).fetchone()
                conn.close()
                if result:
                    resp = make_response(redirect("/forum"))
                    resp.set_cookie("username", username)
                    return resp
            finally:
                error_message = "Invalid credentials"

    return render_template_string(
        """
    <form method="POST">
        <input name="username" placeholder="Username">
        <input name="password" type="password" placeholder="Password">
        <button type="submit">Login</button>
        {% if error %}
            <p style="color:red;">{{ error }}</p>
        {% endif %}
    </form>
    """,
        error=error_message,
    )


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")
