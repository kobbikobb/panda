"""Memory implementations for agent conversation history."""

import os
import sqlite3
from abc import abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass
class Message:
    role: str
    content: str


class Memory(Protocol):
    @abstractmethod
    def add(self, role: str, content: str) -> None: ...

    @abstractmethod
    def get_context(self, max_tokens: int | None = None) -> list[Message]: ...

    @abstractmethod
    def clear(self) -> None: ...


class BufferMemory:
    def __init__(self, max_messages: int | None = None):
        self._messages: list[Message] = []
        self._max_messages = max_messages

    def add(self, role: str, content: str) -> None:
        self._messages.append(Message(role=role, content=content))
        if self._max_messages and len(self._messages) > self._max_messages:
            self._messages = self._messages[-self._max_messages :]

    def get_context(self, max_tokens: int | None = None) -> list[Message]:
        return list(self._messages)

    def clear(self) -> None:
        self._messages.clear()


class SlidingWindowMemory:
    def __init__(
        self,
        max_messages: int = 10,
        keep_recent: int | None = None,
    ):
        self._messages: list[Message] = []
        self._max_messages = max_messages
        self._keep_recent = keep_recent or (max_messages // 2)

    def add(self, role: str, content: str) -> None:
        self._messages.append(Message(role=role, content=content))
        if len(self._messages) > self._max_messages:
            to_drop = len(self._messages) - self._max_messages
            self._messages = self._messages[to_drop:]

    def get_context(self, max_tokens: int | None = None) -> list[Message]:
        return list(self._messages)

    def clear(self) -> None:
        self._messages.clear()


class SQLiteMemory:
    def __init__(
        self,
        db_path: str | None = None,
        max_messages: int = 20,
    ):
        if db_path is None:
            db_path = os.path.expanduser("~/.panda/conversations.db")

        self._db_path = db_path
        self._max_messages = max_messages
        self._init_db()

    def _init_db(self) -> None:
        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    chat_id INTEGER PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (chat_id) REFERENCES users(chat_id)
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_chat_id ON messages(chat_id)")
            conn.commit()

    def _get_or_create_user(self, chat_id: int) -> None:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                "INSERT OR IGNORE INTO users (chat_id) VALUES (?)",
                (chat_id,),
            )
            conn.commit()

    def add(self, role: str, content: str, chat_id: int) -> None:
        self._get_or_create_user(chat_id)
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                "INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)",
                (chat_id, role, content),
            )
            conn.commit()

        self._trim_messages(chat_id)

    def _trim_messages(self, chat_id: int) -> None:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """
                DELETE FROM messages
                WHERE chat_id = ? AND id NOT IN (
                    SELECT id FROM messages
                    WHERE chat_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                )
                """,
                (chat_id, chat_id, self._max_messages),
            )
            conn.commit()

    def get_context(self, chat_id: int, max_tokens: int | None = None) -> list[Message]:
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT role, content FROM messages
                WHERE chat_id = ?
                ORDER BY created_at ASC
                LIMIT ?
                """,
                (chat_id, self._max_messages),
            )
            rows = cursor.fetchall()
            return [Message(role=row["role"], content=row["content"]) for row in rows]

    def clear(self, chat_id: int) -> None:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
            conn.commit()
