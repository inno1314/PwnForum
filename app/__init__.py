from flask import Flask
import shutil
import os
from dotenv import load_dotenv
from config import VulnConfig, FixConfig
from database import ForumDatabase


app = Flask(__name__)

mode = os.getenv("APP_MODE", "vuln")
print(f"* Running in {mode} mode")

if mode == "vuln":
    app.config.from_object(VulnConfig)
else:
    app.config.from_object(FixConfig)

UPLOAD_FOLDER = app.config["UPLOAD_FOLDER"]

load_dotenv()
db = ForumDatabase()


def create_app():
    shutil.rmtree("app/" + UPLOAD_FOLDER)
    os.makedirs("app/" + UPLOAD_FOLDER, exist_ok=True)
    db._drop_db()
    db._init_db()

    from .auth.routes_vuln import auth_bp as auth_vuln_bp
    from .auth.routes_fix import auth_bp as auth_fix_bp

    from .forum.routes_vuln import forum_bp as forum_vuln_bp
    from .forum.routes_fix import forum_bp as forum_fix_bp

    from .lfi.routes_vuln import lfi_bp as lfi_vuln_bp
    from .lfi.routes_fix import lfi_bp as lfi_fix_bp

    from .drafts.routes_vuln import drafts_bp as drafts_vuln_bp
    from .drafts.routes_fix import drafts_bp as drafts_fix_bp

    if mode == "vuln":
        app.register_blueprint(auth_vuln_bp)
        app.register_blueprint(forum_vuln_bp)
        app.register_blueprint(lfi_vuln_bp)
        app.register_blueprint(drafts_vuln_bp)
    if mode == "fix":
        app.register_blueprint(auth_fix_bp)
        app.register_blueprint(forum_fix_bp)
        app.register_blueprint(lfi_fix_bp)
        app.register_blueprint(drafts_fix_bp)

    return app
