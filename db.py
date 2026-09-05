import sqlite3
from typing import Optional

DB_PATH = "captions.db"


def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def get_caption() -> Optional[str]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT value FROM settings WHERE key = 'caption'")
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


def set_caption(text: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO settings (key, value) VALUES ('caption', ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """,
        (text,),
    )
    conn.commit()
    conn.close()


def clear_caption() -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM settings WHERE key = 'caption'")
    conn.commit()
    conn.close()
