from flask import Blueprint, request, redirect
import sqlite3
from datetime import datetime

forum_bp = Blueprint("forum_vuln", __name__)

DB_PATH = "app/db.sqlite3"


@forum_bp.route("/forum", methods=["GET", "POST"])
def forum():
    username = request.cookies.get("username")
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

    html = f"""
    <!DOCTYPE html>
    <html>
    <head><title>Forum (Vulnerable)</title></head>
    <body>
    <h2>Welcome, {username}</h2>
    <a href="/logout">Logout</a>
    <a href="/view">View Changelog</a>

    <form method="POST">
        <input name="content" placeholder="Say something...">
        <button type="submit">Post</button>
    </form>

    <hr>
    <h3>Posts:</h3>
    """

    for post_user, content, timestamp in posts:
        html += f"""
        <div style='margin-bottom: 1em;'>
        <b>{post_user}</b> at {timestamp}<br>
        {content}
        </div>
        """

    html += "</body></html>"

    return html
