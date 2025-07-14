import sqlite3
from datetime import datetime
from typing import Any


class ForumDatabase:
    def __init__(self, db_path="app/db.sqlite3"):
        self.db_path = db_path
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._connect() as conn:
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    content TEXT,
                    timestamp TEXT,
                    file_path TEXT
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS drafts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    content TEXT,
                    file_path TEXT
                )
            """)
            conn.commit()

    def _drop_db(self):
        with self._connect() as conn:
            conn.execute("DROP TABLE IF EXISTS users")
            conn.execute("DROP TABLE IF EXISTS posts")
            conn.execute("DROP TABLE IF EXISTS drafts")

    def is_user_exists(self, username):
        with self._connect() as conn:
            user = conn.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            ).fetchone()
            return user is not None

    def add_user(self, username, password):
        try:
            with self._connect() as conn:
                conn.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, password),
                )
            return True
        except sqlite3.IntegrityError:
            return False

    def get_user_password(self, username):
        with self._connect() as conn:
            row = conn.execute(
                "SELECT password FROM users WHERE username = ?", (username,)
            ).fetchone()
            return row[0] if row else None

    def add_post(self, username, content, timestamp=None, file_path=None):
        if not timestamp:
            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO posts (username, content, timestamp, file_path) VALUES (?, ?, ?, ?)",
                (username, content, timestamp, file_path),
            )
            conn.commit()

    def get_all_posts(self):
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT username, content, timestamp, file_path FROM posts ORDER BY timestamp DESC"
            ).fetchall()
            return rows

    def add_draft(self, username, content, file_path=None):
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO drafts (username, content, file_path) VALUES (?, ?, ?)",
                (username, content, file_path),
            )
            conn.commit()

    def get_user_drafts(self, username) -> list[Any]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, username, content, file_path FROM drafts WHERE username = ?",
                (username,),
            ).fetchall()
            return rows

    def publish_draft(self, draft_id):
        with self._connect() as conn:
            row = conn.execute(
                "SELECT username, content, file_path FROM drafts WHERE id = ?",
                (draft_id,),
            ).fetchone()

            if not row:
                return False

            username, content, file_path = row
            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            conn.execute(
                "INSERT INTO posts (username, content, timestamp, file_path) VALUES (?, ?, ?, ?)",
                (username, content, timestamp, file_path),
            )
            conn.execute("DELETE FROM drafts WHERE id = ?", (draft_id,))
            conn.commit()
            return True
