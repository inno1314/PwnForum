from flask import Blueprint, request, render_template_string

lfi_bp = Blueprint("lfi", __name__)


@lfi_bp.route("/view")
def view_file():
    file_path = request.args.get("file", "")
    try:
        with open(f"app/changelogs/{file_path}", "r") as f:
            content = f.read()
    except Exception as e:
        content = f"Error reading file: {str(e)}"

    return render_template_string(f"""
        <h2>File Viewer (Vulnerable)</h2>
        <form>
            <input name="file" placeholder="File name" value="{file_path}">
            <button type="submit">Read</button>
        </form>
        <pre>{content}</pre>
    """)
