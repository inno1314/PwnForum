import os
from flask import (
    Blueprint,
    request,
    render_template,
    redirect,
    session,
    url_for,
    send_from_directory,
)
from datetime import datetime

from database import ForumDatabase
from app import UPLOAD_FOLDER


forum_bp = Blueprint("forum_fix", __name__, template_folder="../templates/fix")

db = ForumDatabase()


@forum_bp.route("/forum", methods=["GET", "POST"])
def forum():
    username = session.get("username")
    if not username or not db.is_user_exists(username):
        return redirect("/")

    if request.method == "POST":
        content = request.form["content"]
        timestamp = datetime.utcnow().isoformat(" ")

        db.add_post(username, content, timestamp, None)

    posts = db.get_all_posts()

    return render_template(
        "forum.html",
        posts=posts,
        username=username,
    )
