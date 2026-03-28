"""Tests for the memory module."""

import os
import tempfile

import pytest

from src.memory import BufferMemory, SlidingWindowMemory, SQLiteMemory


class TestBufferMemory:
    def test_add_and_get_context(self):
        memory = BufferMemory()
        memory.add("user", "Hello")
        memory.add("assistant", "Hi there")

        context = memory.get_context()
        assert len(context) == 2
        assert context[0].role == "user"
        assert context[0].content == "Hello"
        assert context[1].role == "assistant"
        assert context[1].content == "Hi there"

    def test_max_messages(self):
        memory = BufferMemory(max_messages=3)
        for i in range(5):
            memory.add("user", f"Message {i}")

        context = memory.get_context()
        assert len(context) == 3
        assert context[0].content == "Message 2"

    def test_clear(self):
        memory = BufferMemory()
        memory.add("user", "Hello")
        memory.clear()

        assert len(memory.get_context()) == 0

    def test_message_order_preserved(self):
        memory = BufferMemory()
        memory.add("user", "First")
        memory.add("assistant", "Response 1")
        memory.add("user", "Second")
        memory.add("assistant", "Response 2")

        context = memory.get_context()
        assert len(context) == 4
        assert context[0].content == "First"
        assert context[1].content == "Response 1"
        assert context[2].content == "Second"
        assert context[3].content == "Response 2"


class TestSlidingWindowMemory:
    def test_sliding_window(self):
        memory = SlidingWindowMemory(max_messages=4)
        for i in range(6):
            memory.add("user", f"Message {i}")

        context = memory.get_context()
        assert len(context) == 4
        assert context[0].content == "Message 2"

    def test_default_max(self):
        memory = SlidingWindowMemory()
        for i in range(15):
            memory.add("user", f"Message {i}")

        context = memory.get_context()
        assert len(context) == 10

    def test_clear(self):
        memory = SlidingWindowMemory()
        memory.add("user", "Hello")
        memory.clear()

        assert len(memory.get_context()) == 0


class TestSQLiteMemory:
    @pytest.fixture
    def temp_db(self):
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)

    def test_add_and_get_context(self, temp_db):
        memory = SQLiteMemory(db_path=temp_db, max_messages=20)
        chat_id = 12345

        memory.add("user", "Hello", chat_id)
        memory.add("assistant", "Hi there", chat_id)

        context = memory.get_context(chat_id)
        assert len(context) == 2
        assert context[0].role == "user"
        assert context[0].content == "Hello"
        assert context[1].role == "assistant"
        assert context[1].content == "Hi there"

    def test_multiple_users_isolated(self, temp_db):
        memory = SQLiteMemory(db_path=temp_db, max_messages=20)

        memory.add("user", "User A message", chat_id=111)
        memory.add("assistant", "User A response", chat_id=111)

        memory.add("user", "User B message", chat_id=222)
        memory.add("assistant", "User B response", chat_id=222)

        context_a = memory.get_context(111)
        context_b = memory.get_context(222)

        assert len(context_a) == 2
        assert context_a[0].content == "User A message"
        assert context_a[1].content == "User A response"

        assert len(context_b) == 2
        assert context_b[0].content == "User B message"
        assert context_b[1].content == "User B response"

    def test_max_messages_per_user(self, temp_db):
        memory = SQLiteMemory(db_path=temp_db, max_messages=3)
        chat_id = 12345

        for i in range(5):
            memory.add("user", f"Message {i}", chat_id)

        context = memory.get_context(chat_id)
        assert len(context) == 3
        assert context[0].content == "Message 2"
        assert context[1].content == "Message 3"
        assert context[2].content == "Message 4"

    def test_clear(self, temp_db):
        memory = SQLiteMemory(db_path=temp_db, max_messages=20)
        chat_id = 12345

        memory.add("user", "Hello", chat_id)
        memory.clear(chat_id)

        context = memory.get_context(chat_id)
        assert len(context) == 0

    def test_clear_only_affects_target_user(self, temp_db):
        memory = SQLiteMemory(db_path=temp_db, max_messages=20)

        memory.add("user", "User A message", chat_id=111)
        memory.add("assistant", "User A response", chat_id=111)

        memory.add("user", "User B message", chat_id=222)

        memory.clear(111)

        context_a = memory.get_context(111)
        context_b = memory.get_context(222)

        assert len(context_a) == 0
        assert len(context_b) == 1
        assert context_b[0].content == "User B message"

    def test_message_order_preserved(self, temp_db):
        memory = SQLiteMemory(db_path=temp_db, max_messages=20)
        chat_id = 12345

        memory.add("user", "First", chat_id)
        memory.add("assistant", "Response 1", chat_id)
        memory.add("user", "Second", chat_id)
        memory.add("assistant", "Response 2", chat_id)

        context = memory.get_context(chat_id)
        assert len(context) == 4
        assert context[0].content == "First"
        assert context[1].content == "Response 1"
        assert context[2].content == "Second"
        assert context[3].content == "Response 2"

    def test_empty_context_for_new_user(self, temp_db):
        memory = SQLiteMemory(db_path=temp_db, max_messages=20)
        chat_id = 99999

        context = memory.get_context(chat_id)
        assert len(context) == 0

    def test_default_db_path(self):
        memory = SQLiteMemory()
        assert memory._db_path == os.path.expanduser("~/.panda/conversations.db")

    def test_custom_db_path(self, temp_db):
        custom_path = temp_db.replace(".db", "_custom.db")
        memory = SQLiteMemory(db_path=custom_path)
        assert memory._db_path == custom_path
