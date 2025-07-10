from flask import Flask
import os
from dotenv import load_dotenv
from config import VulnConfig, FixConfig
from db_init import init_db, drop_db


load_dotenv()


def create_app():
    app = Flask(__name__)

    mode = os.getenv("APP_MODE", "vuln")
    print(f"Running in {mode} mode")

    init_db()

    if mode == "vuln":
        app.config.from_object(VulnConfig)
    else:
        app.config.from_object(FixConfig)

    from .auth.routes_vuln import auth_bp as auth_vuln_bp
    from .auth.routes_fix import auth_bp as auth_fix_bp

    from .posting.routes_vuln import forum_bp as forum_vuln_bp
    from .posting.routes_fix import forum_bp as forum_fix_bp

    from .lfi.routes_vuln import lfi_bp as lfi_vuln_bp
    from .lfi.routes_fix import lfi_bp as lfi_fix_bp

    if mode == "vuln":
        app.register_blueprint(auth_vuln_bp)
        app.register_blueprint(forum_vuln_bp)
        app.register_blueprint(lfi_vuln_bp)
    if mode == "fix":
        app.register_blueprint(auth_fix_bp)
        app.register_blueprint(forum_fix_bp)
        app.register_blueprint(lfi_fix_bp)

    return app
