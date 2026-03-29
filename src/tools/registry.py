"""Tool system for agent extensibility."""

from typing import Any
from pydantic import ValidationError

from .base import Tool, ToolResult

_INVOKE_FORMAT = (
    "To use a tool, respond with:\n"
    '<invoke name="tool_name">\n'
    '<parameter name="arg1">value</parameter>\n'
    "</invoke>"
)


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def list_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": t.name,
                "description": t.description,
                "parameters": t.params_class.model_json_schema(),
            }
            for t in self._tools.values()
        ]

    def get_tools_prompt(self) -> str:
        if not self._tools:
            return ""
        lines = ["You have access to the following tools:"]
        for tool in self._tools.values():
            lines.append(f"- {tool.name}: {tool.description}")
        lines.append("")
        lines.append(_INVOKE_FORMAT)
        return "\n".join(lines)

    async def execute(self, name: str, params: dict[str, Any]) -> ToolResult:
        tool = self.get(name)
        if tool is None:
            return ToolResult.fail(f"Tool not found: {name}")
        try:
            tool_params = tool.params_class.model_validate(params)
            return await tool.execute(tool_params)
        except ValidationError as exec:
            return ToolResult.fail(f"Param validation failed: {exec}")
