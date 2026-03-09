"""Tests for the Agent module."""

from unittest.mock import AsyncMock

import pytest

from src.agent import Agent
from src.llm import LLMError


class MockLLMClient:
    def __init__(self, response: str = "Mock response", should_fail: bool = False):
        self._response = response
        self._should_fail = should_fail
        self.generate = AsyncMock()

        async def generate_wrapper(prompt: str, system_prompt: str | None = None) -> str:
            if self._should_fail:
                raise LLMError("Mock LLM error")
            return self._response

        self.generate.side_effect = generate_wrapper


class TestAgent:
    @pytest.mark.asyncio
    async def test_process_returns_llm_response(self):
        mock_llm = MockLLMClient(response="Hello, world!")
        agent = Agent(llm_client=mock_llm, system_prompt="You are helpful.")

        result = await agent.process("Hi there")

        assert result == "Hello, world!"

    @pytest.mark.asyncio
    async def test_process_uses_system_prompt(self):
        mock_llm = MockLLMClient(response="Contextual response")
        agent = Agent(llm_client=mock_llm, system_prompt="You are a pirate.")

        await agent.process("Hello")

        mock_llm.generate.assert_called_once()
        call_kwargs = mock_llm.generate.call_args.kwargs
        assert call_kwargs["system_prompt"] == "You are a pirate."

    @pytest.mark.asyncio
    async def test_process_propagates_llm_error(self):
        mock_llm = MockLLMClient(should_fail=True)
        agent = Agent(llm_client=mock_llm)

        with pytest.raises(LLMError):
            await agent.process("Hi")

    @pytest.mark.asyncio
    async def test_process_without_system_prompt(self):
        mock_llm = MockLLMClient(response="Response")
        agent = Agent(llm_client=mock_llm)

        await agent.process("Hello")

        call_kwargs = mock_llm.generate.call_args.kwargs
        assert call_kwargs["system_prompt"] is None
