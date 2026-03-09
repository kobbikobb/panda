"""Tool system for agent extensibility."""

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass
class ToolResult:
    success: bool
    result: Any
    error: str | None = None


class Tool(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def description(self) -> str: ...

    async def execute(self, **kwargs) -> ToolResult: ...


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def list_tools(self) -> list[dict[str, str]]:
        return [{"name": t.name, "description": t.description} for t in self._tools.values()]

    def get_tools_prompt(self) -> str:
        if not self._tools:
            return ""
        lines = ["You have access to the following tools:"]
        for tool in self._tools.values():
            lines.append(f"- {tool.name}: {tool.description}")
        lines.append("")
        lines.append("To use a tool, respond with:")
        lines.append('<invoke name="tool_name">')
        lines.append('<parameter name="arg1">value</parameter>')
        lines.append("</invoke>")
        return "\n".join(lines)
