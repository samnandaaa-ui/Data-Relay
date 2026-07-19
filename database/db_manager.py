"""
database/db_manager.py
Mengelola koneksi SQLite: membuat file & tabel kalau belum ada (init),
lalu menyediakan satu koneksi yang dipakai ulang oleh models/.
"""

import sqlite3
import os
from config.settings import get_db_path

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


class DatabaseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._connection = None
        return cls._instance

    def get_connection(self):
        if self._connection is None:
            db_path = get_db_path()
            self._connection = sqlite3.connect(db_path)
            self._connection.execute("PRAGMA foreign_keys = ON")
            self._connection.row_factory = sqlite3.Row
            self._init_schema()
        return self._connection

    def _init_schema(self):
        """Jalankan schema.sql. Aman dipanggil berkali-kali (semua CREATE TABLE pakai IF NOT EXISTS)."""
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        self._connection.executescript(schema_sql)
        self._connection.commit()

    def close(self):
        if self._connection is not None:
            self._connection.close()
            self._connection = None


db_manager = DatabaseManager()
