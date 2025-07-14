import os
from flask import Blueprint, request, redirect, session
from app import UPLOAD_FOLDER
from database import ForumDatabase
from datetime import datetime

forum_bp = Blueprint("forum_vuln", __name__)
db = ForumDatabase()


@forum_bp.route("/forum", methods=["GET", "POST"])
def forum():
    username = request.cookies.get("username")
    if not username:
        return redirect("/")

    if request.method == "POST":
        content = request.form.get("content")
        timestamp = datetime.utcnow().isoformat(" ")
        if content:
            db.add_post(username, content, timestamp, None)

    posts = db.get_all_posts()

    html = f"""
    <!DOCTYPE html>
    <html>
    <head><title>Forum (Vulnerable)</title></head>
    <body>
    <h2>Welcome, {username}</h2>
    <a href="/logout">Logout</a>
    <a href="/view">View Changelog</a>
    <a href="/drafts/{username}">Your Drafts</a>
    <form method="POST">
        <input name="content" placeholder="Say something...">
        <button type="submit">Post</button>
    </form>
    <hr>
    <h3>Posts:</h3>
    """

    for post_user, content, timestamp, file_path in posts:
        html += f"""
        <div style='margin-bottom: 1em;'>
            <b>{post_user}</b> at {timestamp}<br>
            {content}<br>
            {f'<img src="{os.path.join(UPLOAD_FOLDER, file_path)}" style="max-width: 300px;">' if file_path and file_path.lower().endswith((".png", ".jpg", ".jpeg", ".gif")) else ""}
            {f'<a href="{file_path}" download>Download file</a>' if file_path and not file_path.lower().endswith((".png", ".jpg", ".jpeg", ".gif")) else ""}
        </div>
        """
    html += "</body></html>"

    return html
