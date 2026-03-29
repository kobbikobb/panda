"""Base for tools"""

from dataclasses import dataclass
from typing import Any, Protocol

from pydantic import BaseModel


@dataclass
class ToolResult:
    success: bool
    result: Any
    error: str | None = None

    @classmethod
    def ok(cls, result: Any) -> ToolResult:
        return cls(success=True, result=result)

    @classmethod
    def fail(cls, error: str) -> ToolResult:
        return cls(success=False, result=None, error=error)


class ToolParams(BaseModel):
    """Base class for typed tools for parameters"""

    model_config = {"extra": "forbid"}


class Tool(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def description(self) -> str: ...

    @property
    def params_class(self) -> type[ToolParams]: ...

    async def execute(self, params: ToolParams) -> ToolResult: ...
