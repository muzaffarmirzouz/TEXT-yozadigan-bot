import os
import sqlite3
from typing import List, Optional, Tuple

# Railway'da bu Volume mount qilingan doimiy papkaga ko'rsatilishi kerak
# (masalan /data/captions.db), aks holda har deploy'da ma'lumot o'chib ketadi.
DB_PATH = os.getenv("DB_PATH", "captions.db")


def _column_exists(cur: sqlite3.Cursor, table: str, column: str) -> bool:
    cur.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cur.fetchall())


def init_db() -> None:
    db_dir = os.path.dirname(DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS channels (
            channel_id INTEGER PRIMARY KEY,
            title TEXT,
            owner_id INTEGER
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
    # Eski (omma uchun ochilishidan oldingi) bazalarda "channels" jadvalida
    # owner_id ustuni bo'lmasligi mumkin — uni qo'shib qo'yamiz.
    if not _column_exists(cur, "channels", "owner_id"):
        cur.execute("ALTER TABLE channels ADD COLUMN owner_id INTEGER")
    # Har bir kanal uchun o'girish yo'nalishi (lotin->kirill / kirill->lotin
    # / o'chirilgan). SQLite ALTER TABLE ... DEFAULT eski qatorlarga ham
    # avtomatik shu qiymatni beradi.
    if not _column_exists(cur, "channels", "translit_mode"):
        cur.execute("ALTER TABLE channels ADD COLUMN translit_mode TEXT DEFAULT 'l2c'")
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


def assign_default_owner(default_owner_id: Optional[int]) -> None:
    """Omma uchun ochilishidan oldin ro'yxatga olingan, egasi noma'lum
    (owner_id = NULL) kanallarni berilgan foydalanuvchiga bog'laydi
    (bir martalik migratsiya, botning ilk operatoriga)."""
    if not default_owner_id:
        return
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "UPDATE channels SET owner_id = ? WHERE owner_id IS NULL",
        (default_owner_id,),
    )
    conn.commit()
    conn.close()


def register_channel(channel_id: int, title: str, owner_id: int) -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO channels (channel_id, title, owner_id) VALUES (?, ?, ?) "
        "ON CONFLICT(channel_id) DO UPDATE SET title = excluded.title, owner_id = excluded.owner_id",
        (channel_id, title, owner_id),
    )
    conn.commit()
    conn.close()


def remove_channel(channel_id: int) -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM channels WHERE channel_id = ?", (channel_id,))
    cur.execute("DELETE FROM captions WHERE channel_id = ?", (channel_id,))
    conn.commit()
    conn.close()


def list_channels_for_owner(owner_id: int) -> List[Tuple[int, str]]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT channel_id, title FROM channels WHERE owner_id = ? ORDER BY title",
        (owner_id,),
    )
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


def get_translit_mode(channel_id: int) -> str:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT translit_mode FROM channels WHERE channel_id = ?", (channel_id,))
    row = cur.fetchone()
    conn.close()
    return (row[0] if row and row[0] else "l2c")


def set_translit_mode(channel_id: int, mode: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "UPDATE channels SET translit_mode = ? WHERE channel_id = ?",
        (mode, channel_id),
    )
    conn.commit()
    conn.close()


def get_channel_owner(channel_id: int) -> Optional[int]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT owner_id FROM channels WHERE channel_id = ?", (channel_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


def count_channels() -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM channels")
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 0


def count_owners() -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(DISTINCT owner_id) FROM channels WHERE owner_id IS NOT NULL")
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 0


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
