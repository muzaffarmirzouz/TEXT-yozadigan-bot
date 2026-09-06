import sqlite3
from typing import List, Optional, Tuple

DB_PATH = "captions.db"


def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS channels (
            channel_id INTEGER PRIMARY KEY,
            title TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS captions (
            channel_id INTEGER PRIMARY KEY,
            caption TEXT
        )
        """
    )
    # Eski (bitta kanalli) versiyadan qolgan jadval — migratsiya uchun kerak
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


def migrate_legacy_caption(channel_id: Optional[int]) -> None:
    """Eski bir-kanalli versiyada saqlangan izohni shu kanal uchun ko'chiradi (bir martalik)."""
    if not channel_id:
        return
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT value FROM settings WHERE key = 'caption'")
    row = cur.fetchone()
    if row and row[0]:
        cur.execute(
            "INSERT INTO captions (channel_id, caption) VALUES (?, ?) "
            "ON CONFLICT(channel_id) DO NOTHING",
            (channel_id, row[0]),
        )
        conn.commit()
    conn.close()


def register_channel(channel_id: int, title: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO channels (channel_id, title) VALUES (?, ?) "
        "ON CONFLICT(channel_id) DO UPDATE SET title = excluded.title",
        (channel_id, title),
    )
    conn.commit()
    conn.close()


def remove_channel(channel_id: int) -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM channels WHERE channel_id = ?", (channel_id,))
    conn.commit()
    conn.close()


def list_channels() -> List[Tuple[int, str]]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT channel_id, title FROM channels ORDER BY title")
    rows = cur.fetchall()
    conn.close()
    return rows


def get_channel_title(channel_id: int) -> Optional[str]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT title FROM channels WHERE channel_id = ?", (channel_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


def get_caption(channel_id: int) -> Optional[str]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT caption FROM captions WHERE channel_id = ?", (channel_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


def set_caption(channel_id: int, text: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO captions (channel_id, caption) VALUES (?, ?) "
        "ON CONFLICT(channel_id) DO UPDATE SET caption = excluded.caption",
        (channel_id, text),
    )
    conn.commit()
    conn.close()


def clear_caption(channel_id: int) -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM captions WHERE channel_id = ?", (channel_id,))
    conn.commit()
    conn.close()
