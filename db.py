"""
Jednoduchá SQLite vrstva pro ukládání měsíčních snapshotů počtu sledujících
a počtu příspěvků.
"""
import sqlite3
from datetime import date
from pathlib import Path

DB_PATH = Path(__file__).parent / "followers.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS accounts (
            username TEXT PRIMARY KEY,
            type TEXT NOT NULL CHECK (type IN ('own', 'foreign'))
        );

        CREATE TABLE IF NOT EXISTS snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL REFERENCES accounts(username),
            snapshot_date TEXT NOT NULL,
            followers INTEGER NOT NULL,
            posts INTEGER,
            UNIQUE(username, snapshot_date)
        );
        """
    )

    # migrace starších databází, které sloupec 'posts' ještě nemají
    cols = [r[1] for r in conn.execute("PRAGMA table_info(snapshots)").fetchall()]
    if "posts" not in cols:
        conn.execute("ALTER TABLE snapshots ADD COLUMN posts INTEGER")

    conn.commit()
    conn.close()


def ensure_account(username: str, acc_type: str):
    conn = get_connection()
    conn.execute(
        "INSERT INTO accounts (username, type) VALUES (?, ?) "
        "ON CONFLICT(username) DO UPDATE SET type=excluded.type",
        (username, acc_type),
    )
    conn.commit()
    conn.close()


def insert_snapshot(username: str, followers: int, snapshot_date: str = None,
                    posts: int = None):
    snapshot_date = snapshot_date or date.today().isoformat()
    conn = get_connection()
    conn.execute(
        "INSERT INTO snapshots (username, snapshot_date, followers, posts) "
        "VALUES (?, ?, ?, ?) "
        "ON CONFLICT(username, snapshot_date) DO UPDATE SET "
        "followers=excluded.followers, posts=excluded.posts",
        (username, snapshot_date, followers, posts),
    )
    conn.commit()
    conn.close()


def get_latest_two_snapshots(username: str):
    """Vrátí posledních 5 záznamů (nejnovější první) pro daný účet."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT snapshot_date, followers FROM snapshots "
        "WHERE username = ? ORDER BY snapshot_date DESC LIMIT 5",
        (username,),
    ).fetchall()
    conn.close()
    return rows


def get_all_accounts():
    conn = get_connection()
    rows = conn.execute("SELECT username, type FROM accounts ORDER BY username").fetchall()
    conn.close()
    return rows
