from __future__ import annotations

import logging
import sqlite3
from typing import Optional

from fastapi import HTTPException

from . import config

logger = logging.getLogger(__name__)


def get_connection() -> sqlite3.Connection:
    config.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now'))
                );
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS action_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    note_id INTEGER,
                    text TEXT NOT NULL,
                    done INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (note_id) REFERENCES notes(id)
                );
                """
            )
            conn.commit()
    except sqlite3.Error as exc:
        logger.exception("Failed to initialize database")
        raise RuntimeError("Database initialization failed") from exc


def insert_note(content: str) -> int:
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO notes (content) VALUES (?)", (content,))
            conn.commit()
            return int(cursor.lastrowid)
    except sqlite3.Error as exc:
        logger.exception("insert_note failed")
        raise HTTPException(status_code=500, detail="Database error") from exc


def list_notes() -> list[sqlite3.Row]:
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, content, created_at FROM notes ORDER BY id DESC")
            return list(cursor.fetchall())
    except sqlite3.Error as exc:
        logger.exception("list_notes failed")
        raise HTTPException(status_code=500, detail="Database error") from exc


def get_note(note_id: int) -> Optional[sqlite3.Row]:
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, content, created_at FROM notes WHERE id = ?",
                (note_id,),
            )
            return cursor.fetchone()
    except sqlite3.Error as exc:
        logger.exception("get_note failed for id=%s", note_id)
        raise HTTPException(status_code=500, detail="Database error") from exc


def insert_action_items(items: list[str], note_id: Optional[int] = None) -> list[int]:
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            ids: list[int] = []
            for item in items:
                cursor.execute(
                    "INSERT INTO action_items (note_id, text) VALUES (?, ?)",
                    (note_id, item),
                )
                ids.append(int(cursor.lastrowid))
            conn.commit()
            return ids
    except sqlite3.Error as exc:
        logger.exception("insert_action_items failed")
        raise HTTPException(status_code=500, detail="Database error") from exc


def list_action_items(note_id: Optional[int] = None) -> list[sqlite3.Row]:
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            if note_id is None:
                cursor.execute(
                    "SELECT id, note_id, text, done, created_at FROM action_items ORDER BY id DESC"
                )
            else:
                cursor.execute(
                    "SELECT id, note_id, text, done, created_at FROM action_items"
                    " WHERE note_id = ? ORDER BY id DESC",
                    (note_id,),
                )
            return list(cursor.fetchall())
    except sqlite3.Error as exc:
        logger.exception("list_action_items failed")
        raise HTTPException(status_code=500, detail="Database error") from exc


def mark_action_item_done(action_item_id: int, done: bool) -> None:
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE action_items SET done = ? WHERE id = ?",
                (1 if done else 0, action_item_id),
            )
            conn.commit()
    except sqlite3.Error as exc:
        logger.exception("mark_action_item_done failed for id=%s", action_item_id)
        raise HTTPException(status_code=500, detail="Database error") from exc
