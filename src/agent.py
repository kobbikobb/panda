"""Agent for orchestrating LLM interactions.

Keep comments lean. Code should speak for itself.
"""

from src.llm import LLMClient
from src.memory import Memory
from src.tools import ToolRegistry


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

    async def process(self, user_message: str) -> str:
        full_prompt = self._build_prompt(user_message)
        response = await self._llm_client.generate(prompt=full_prompt)

        if self._memory:
            self._memory.add("user", user_message)
            self._memory.add("assistant", response)

        return response

    def _build_prompt(self, user_message: str) -> str:
        parts = []

        if self._system_prompt:
            parts.append(self._system_prompt)

        if self._memory:
            context = self._memory.get_context()
            if context:
                conversation = "\n".join(f"{msg.role}: {msg.content}" for msg in context)
                parts.append(f"Conversation history:\n{conversation}")

        if self._tools:
            tools_prompt = self._tools.get_tools_prompt()
            if tools_prompt:
                parts.append(tools_prompt)

        parts.append(f"User: {user_message}")
        return "\n\n".join(parts)
