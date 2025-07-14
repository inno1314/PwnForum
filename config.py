import os


class Config:
    SECRET_KEY = os.urandom(32)
    DATABASE = os.path.join(os.getcwd(), "app", "db.sqlite3")
    UPLOAD_FOLDER = "static/uploads"


class VulnConfig(Config):
    MODE = "vuln"


class FixConfig(Config):
    MODE = "fix"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # True для HTTPS
    SESSION_COOKIE_SAMESITE = "Lax"
