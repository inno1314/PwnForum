from flask import Blueprint, request, render_template, redirect, session
import sqlite3
from datetime import datetime

forum_bp = Blueprint("forum_fix", __name__, template_folder="../templates/fix")

DB_PATH = "app/db.sqlite3"


@forum_bp.route("/forum", methods=["GET", "POST"])
def forum():
    username = session.get("username")
    if not username:
        return redirect("/")

    conn = sqlite3.connect("app/db.sqlite3")
    c = conn.cursor()

    if request.method == "POST":
        content = request.form["content"]
        timestamp = datetime.utcnow().isoformat(" ")

        c.execute(
            "INSERT INTO posts (username, content, timestamp) VALUES (?, ?, ?)",
            (username, content, timestamp),
        )
        conn.commit()

    c.execute("SELECT username, content, timestamp FROM posts ORDER BY timestamp DESC")
    posts = c.fetchall()
    conn.close()

    return render_template("forum.html", posts=posts, username=username)
