import os
import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).parent.parent / "data" / "deviceops.db"
DB_PATH = Path(os.environ.get("DEVICEOPS_DB_PATH", str(DEFAULT_DB_PATH)))

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            profile TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'idle',
            current_version TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS firmware_builds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version TEXT NOT NULL,
            upload_status TEXT NOT NULL DEFAULT 'uploaded'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ota_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id INTEGER NOT NULL,
            build_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            started_at TEXT,
            completed_at TEXT,
            FOREIGN KEY (device_id) REFERENCES devices(id),
            FOREIGN KEY (build_id) REFERENCES firmware_builds(id)
        )
    """)

    conn.commit()
    conn.close()