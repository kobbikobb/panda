"""Tests for the Agent module."""

from unittest.mock import AsyncMock

import pytest

from src.agent import Agent
from src.llm import LLMError
from src.memory import BufferMemory
from src.tools import ToolRegistry, ToolResult


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
        memory = BufferMemory()
        agent = Agent(llm_client=mock_llm, memory=memory, system_prompt="You are helpful.")

        result = await agent.process("Hi there")

        assert result == "Hello, world!"

    @pytest.mark.asyncio
    async def test_process_saves_to_memory(self):
        mock_llm = MockLLMClient(response="Response")
        memory = BufferMemory()
        agent = Agent(llm_client=mock_llm, memory=memory)

        await agent.process("Hello")
        await agent.process("How are you?")

        context = memory.get_context()
        assert len(context) == 4  # 2 user + 2 assistant

    @pytest.mark.asyncio
    async def test_process_propagates_llm_error(self):
        mock_llm = MockLLMClient(should_fail=True)
        memory = BufferMemory()
        agent = Agent(llm_client=mock_llm, memory=memory)

        with pytest.raises(LLMError):
            await agent.process("Hi")

    @pytest.mark.asyncio
    async def test_process_builds_prompt_with_context(self):
        mock_llm = MockLLMClient(response="Response")
        memory = BufferMemory()
        memory.add("user", "Previous message")
        memory.add("assistant", "Previous response")
        agent = Agent(llm_client=mock_llm, memory=memory, system_prompt="You are helpful.")

        await agent.process("New message")

        mock_llm.generate.assert_called_once()
        call_args = mock_llm.generate.call_args
        assert "Previous message" in call_args.kwargs["prompt"]
        assert "New message" in call_args.kwargs["prompt"]


class TestBufferMemory:
    def test_add_and_get_context(self):
        memory = BufferMemory()
        memory.add("user", "Hello")
        memory.add("assistant", "Hi there")

        context = memory.get_context()
        assert len(context) == 2
        assert context[0].role == "user"

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


class TestToolRegistry:
    def test_register_and_get(self):
        registry = ToolRegistry()

        class DummyTool:
            name = "test_tool"
            description = "A test tool"

            async def execute(self, **kwargs) -> ToolResult:
                return ToolResult(success=True, result="result")

        registry.register(DummyTool())
        tool = registry.get("test_tool")

        assert tool is not None
        assert tool.name == "test_tool"

    def test_list_tools(self):
        registry = ToolRegistry()

        class DummyTool:
            name = "test_tool"
            description = "A test tool"

            async def execute(self, **kwargs) -> ToolResult:
                return ToolResult(success=True, result="result")

        registry.register(DummyTool())
        tools = registry.list_tools()

        assert len(tools) == 1
        assert tools[0]["name"] == "test_tool"
