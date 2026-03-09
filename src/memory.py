"""Memory implementations for agent conversation history."""

from abc import abstractmethod
from dataclasses import dataclass
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
