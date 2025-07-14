import os
import uuid
import PIL.Image as Image
from flask import Blueprint, request, abort, render_template, url_for, session, redirect
from werkzeug.utils import secure_filename
from database import ForumDatabase
from app import UPLOAD_FOLDER

drafts_bp = Blueprint("drafts", __name__)
db = ForumDatabase()

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}


def is_safe_file(file):
    filename = secure_filename(file.filename)
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


def generate_filename(filename):
    """Generate secure filename with short UUID prefix"""
    safe_name = secure_filename(filename)
    if not safe_name:
        return None
    return f"{uuid.uuid4().hex[:10]}_{safe_name}"


@drafts_bp.route("/drafts", methods=["GET", "POST"])
def drafts():
    username = session["username"]
    if not username or not db.is_user_exists(username):
        return redirect("/")

    if request.method == "POST":
        draft_content = request.form.get("draft_content", "").strip()
        action = request.form.get("action")
        file = request.files.get("file")
        file_path = None

        if file and file.filename:
            if not is_safe_file(file):
                abort(400, "Invalid file type")

            # Generate secure filename
            secure_name = generate_filename(file.filename)
            if not secure_name:
                abort(400, "Invalid filename")

            # Save file
            try:
                save_path = os.path.join("app", UPLOAD_FOLDER, secure_name)
                file.save(save_path)
                file_path = secure_name
            except Exception:
                abort(500, "Error saving file")

        if action == "save" and draft_content:
            db.add_draft(username, draft_content, file_path)
        elif action == "publish":
            drafts_for_user = db.get_user_drafts(username)
            if drafts_for_user:
                draft_id = drafts_for_user[-1][0]
                db.publish_draft(draft_id)

    drafts_for_user = db.get_user_drafts(username)
    drafts_for_user.reverse()

    return render_template(
        "drafts.html",
        username=username,
        drafts=drafts_for_user,
        static_files_path=url_for("static", filename=""),
    )
