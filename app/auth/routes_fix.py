from flask import Blueprint, request, render_template_string, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import ForumDatabase

auth_bp = Blueprint("auth_fix", __name__)
db = ForumDatabase()


@auth_bp.route("/", methods=["GET", "POST"])
def login():
    error_message = ""

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            error_message = "Fill all fields"
        else:
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

    return render_template_string(
        """
    <form method="POST">
        <input name="username" placeholder="Username">
        <input name="password" type="password" placeholder="Password">
        <button type="submit">Login / Register</button>
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
