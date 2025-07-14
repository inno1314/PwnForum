from flask import Blueprint, request, render_template_string
from werkzeug.utils import secure_filename

lfi_bp = Blueprint("lfi", __name__)


@lfi_bp.route("/view")
def view_file():
    user_arg = request.args.get("file", "")
    file_path = secure_filename(user_arg)
    try:
        with open(f"app/changelogs/{file_path}", "r") as f:
            content = f.read()
    except Exception:
        content = "Incorrect input"

    return render_template_string(f"""
        <h2>File Viewer (Fixed)</h2>
        <h3>You can read changelogs by entering version number.</h3>
        <h3>Versions available: from 1 to 4.</h3>
        <a href="/forum">Back to main</a>
        <form>
            <input name="file" placeholder="File name" value="{file_path}">
            <button type="submit">Read</button>
        </form>
        <pre>{content}</pre>
    """)
