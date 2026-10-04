from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


class Database:
    def __init__(self, database_path: Path):
        self.database_path = database_path

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.database_path,
            check_same_thread=False,
        )

        connection.row_factory = sqlite3.Row

        connection.execute("PRAGMA journal_mode=WAL;")
        connection.execute("PRAGMA foreign_keys=ON;")

        return connection

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS groups (
                    chat_id INTEGER PRIMARY KEY,
                    title TEXT,
                    welcome_message TEXT,
                    welcome_image TEXT,
                    default_volume INTEGER NOT NULL DEFAULT 100,
                    max_queue_size INTEGER NOT NULL DEFAULT 50,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS permissions (
                    chat_id INTEGER PRIMARY KEY,
                    pause_resume_admin_only INTEGER NOT NULL DEFAULT 1,
                    stop_end_admin_only INTEGER NOT NULL DEFAULT 1,
                    volume_admin_only INTEGER NOT NULL DEFAULT 1,
                    skip_admin_only INTEGER NOT NULL DEFAULT 0
                );
                """
            )

    def execute(
        self,
        query: str,
        parameters: tuple[Any, ...] = (),
    ) -> None:
        with self.connect() as connection:
            connection.execute(query, parameters)

    def fetch_one(
        self,
        query: str,
        parameters: tuple[Any, ...] = (),
    ) -> sqlite3.Row | None:
        with self.connect() as connection:
            cursor = connection.execute(
                query,
                parameters,
            )

            return cursor.fetchone()

    def fetch_all(
        self,
        query: str,
        parameters: tuple[Any, ...] = (),
    ) -> list[sqlite3.Row]:
        with self.connect() as connection:
            cursor = connection.execute(
                query,
                parameters,
            )

            return cursor.fetchall()

    # -------------------------
    # Group configuration
    # -------------------------

    def ensure_group(
        self,
        chat_id: int,
        title: str | None = None,
    ) -> None:
        self.execute(
            """
            INSERT INTO groups (
                chat_id,
                title
            )
            VALUES (?, ?)
            ON CONFLICT(chat_id)
            DO UPDATE SET
                title = excluded.title,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                chat_id,
                title,
            ),
        )

        self.execute(
            """
            INSERT OR IGNORE INTO permissions (
                chat_id
            )
            VALUES (?)
            """,
            (chat_id,),
        )

    def get_group(
        self,
        chat_id: int,
    ) -> sqlite3.Row | None:
        return self.fetch_one(
            """
            SELECT *
            FROM groups
            WHERE chat_id = ?
            """,
            (chat_id,),
        )

    def set_welcome_message(
        self,
        chat_id: int,
        message: str,
    ) -> None:
        self.execute(
            """
            UPDATE groups
            SET
                welcome_message = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE chat_id = ?
            """,
            (
                message,
                chat_id,
            ),
        )

    def set_welcome_image(
        self,
        chat_id: int,
        image_file_id: str | None,
    ) -> None:
        self.execute(
            """
            UPDATE groups
            SET
                welcome_image = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE chat_id = ?
            """,
            (
                image_file_id,
                chat_id,
            ),
        )

    # -------------------------
    # Global settings
    # -------------------------

    def get_setting(
        self,
        key: str,
        default: str | None = None,
    ) -> str | None:
        row = self.fetch_one(
            """
            SELECT value
            FROM settings
            WHERE key = ?
            """,
            (key,),
        )

        if row is None:
            return default

        return row["value"]

    def set_setting(
        self,
        key: str,
        value: str,
    ) -> None:
        self.execute(
            """
            INSERT INTO settings (
                key,
                value,
                updated_at
            )
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(key)
            DO UPDATE SET
                value = excluded.value,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                key,
                value,
            ),
        )
