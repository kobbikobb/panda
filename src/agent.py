"""Agent for orchestrating LLM interactions.

Keep comments lean. Code should speak for itself.
"""

import re

from src.llm import LLMClient
from src.memory import Memory
from src.tools.tool_registry import ToolRegistry


class Agent:
    def __init__(
        self,
        llm_client: LLMClient,
        memory: Memory | None = None,
        tools: ToolRegistry | None = None,
        system_prompt: str | None = None,
    ):
        self._llm_client = llm_client
        self._memory = memory
        self._tools = tools
        self._system_prompt = system_prompt

    async def process(self, user_message: str, chat_id: int | None = None) -> str:
        return await self._execute_loop(user_message, chat_id)

    async def _execute_loop(self, user_message: str, chat_id: int | None = None) -> str:
        max_iterations = 3
        tool_results: list[str] = []

        for _ in range(max_iterations):
            full_prompt = self._build_prompt(user_message, tool_results, chat_id)
            response = await self._llm_client.generate(prompt=full_prompt)

            if self._memory:
                if chat_id is not None:
                    self._memory.add("user", user_message, chat_id)
                    self._memory.add("assistant", response, chat_id)
                else:
                    self._memory.add("user", user_message)
                    self._memory.add("assistant", response)

            tool_call = self._parse_tool_call(response)
            if not tool_call:
                return response

            result = await self._execute_tool(tool_call["name"], tool_call["args"])
            tool_results.append(f"Tool: {tool_call['name']}\nResult: {result}")

        return "I'm sorry, I couldn't complete that request. Please try again."

    def _parse_tool_call(self, response: str) -> dict | None:
        pattern = r'<invoke name="(\w+)">(.*?)</invoke>'
        match = re.search(pattern, response, re.DOTALL)
        if not match:
            return None

        tool_name = match.group(1)
        args = {}
        arg_pattern = r'<parameter name="(\w+)">(.*?)</parameter>'
        for arg_match in re.finditer(arg_pattern, match.group(2)):
            args[arg_match.group(1)] = arg_match.group(2).strip()

        return {"name": tool_name, "args": args}

    async def _execute_tool(self, name: str, args: dict) -> str:
        if not self._tools:
            return "No tools available."

        tool = self._tools.get(name)
        if not tool:
            return f"Tool '{name}' not found."

        result = await tool.execute(**args)
        if result.success:
            return str(result.result)
        return f"Error: {result.error}"

    def _build_prompt(
        self, user_message: str, tool_results: list[str], chat_id: int | None = None
    ) -> str:
        parts = []

        if self._system_prompt:
            parts.append(self._system_prompt)

        if self._memory:
            if chat_id is not None:
                context = self._memory.get_context(chat_id)
            else:
                context = self._memory.get_context()
            if context:
                conversation = "\n".join(f"{msg.role}: {msg.content}" for msg in context)
                parts.append(f"Conversation history:\n{conversation}")

        if self._tools:
            tools_prompt = self._tools.get_tools_prompt()
            if tools_prompt:
                parts.append(tools_prompt)

        for tr in tool_results:
            parts.append(f"Tool result:\n{tr}")

        parts.append(f"User: {user_message}")
        return "\n\n".join(parts)
