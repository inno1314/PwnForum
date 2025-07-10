import sqlite3

conn = sqlite3.connect("app/db.sqlite3")
c = conn.cursor()


def init_db():
    print("Initializing database...")
    c.execute(
        """CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT
        )"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY,
        username TEXT,
        content TEXT,
        timestamp TEXT
        )"""
    )

    c.execute("INSERT OR IGNORE INTO users VALUES ('admin', 'admin')")
    c.execute("INSERT OR IGNORE INTO users VALUES ('user', 'qwerty')")

    c.execute(
        "INSERT OR IGNORE INTO posts VALUES (1, 'admin', 'Welcome to the forum!', '2025-07-10 00:00:00')"
    )

    conn.commit()
    conn.close()


def drop_db():
    c.execute("DROP TABLE IF EXISTS users")
    c.execute("DROP TABLE IF EXISTS posts")
    conn.commit()
    conn.close()
