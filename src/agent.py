"""Agent for orchestrating LLM interactions.

Keep comments lean. Code should speak for itself.
"""

from src.llm import LLMClient


class Agent:
    def __init__(self, llm_client: LLMClient, system_prompt: str | None = None):
        self._llm_client = llm_client
        self._system_prompt = system_prompt

    async def process(self, user_message: str) -> str:
        return await self._llm_client.generate(
            prompt=user_message,
            system_prompt=self._system_prompt,
        )
