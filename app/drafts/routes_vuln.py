import os
from flask import Blueprint, request
from database import ForumDatabase
from app import UPLOAD_FOLDER

drafts_bp = Blueprint("drafts_vuln", __name__)
db = ForumDatabase()


def is_allowed(filename):
    allowed_extensions = {"png", "jpg", "jpeg"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


@drafts_bp.route("/drafts/<username>", methods=["GET", "POST"])
def drafts(username):
    if request.method == "POST":
        draft_content = request.form.get("draft_content")
        action = request.form.get("action")
        file = request.files.get("file")
        file_path = None
        if file and not file.filename:
            return "Wrong filename", 400

        if file and file.filename and is_allowed(file.filename):
            file_path = os.path.join("app", UPLOAD_FOLDER, file.filename)
            file.save(file_path)

        if action == "save" and draft_content:
            db.add_draft(username, draft_content, file.filename if file else None)
        elif action == "publish":
            drafts_for_user = db.get_user_drafts(username)
            if drafts_for_user:
                draft_id = drafts_for_user[-1][0]
                db.publish_draft(draft_id)

    drafts_for_user = db.get_user_drafts(username)
    drafts_for_user.reverse()

    html = f"""
    <!DOCTYPE html>
    <html>
    <head><title>Your Drafts</title></head>
    <body>
    <h2>Drafts for {username}</h2>
    <a href="/forum">Return to Forum</a>
    <form method="POST" enctype="multipart/form-data">
        <input name="draft_content" placeholder="Write your draft...">
        <input type="file" name="file">
        <button type="submit" name="action" value="save">Save</button>
        <button type="submit" name="action" value="publish">Publish Last Draft</button>
    </form>
    <hr>
    """

    for draft in drafts_for_user:
        html += f"""
        <div style='margin-bottom: 1em;'>
        Draft ID: {draft[0]}<br>
        {draft[2]}<br>
        {f'<a href="{draft[3]}">File</a>' if draft[3] else ""}
        </div>
        """

    html += "</body></html>"
    return html
