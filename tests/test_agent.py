"""Tests for the Agent module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agent import Agent
from src.llm import LLMError
from src.memory import BufferMemory, SlidingWindowMemory
from src.tools import ToolRegistry, ToolResult
from src.tools.web_search import WebSearchTool


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


class TestParseToolCall:
    def test_parse_tool_call_valid(self):
        mock_llm = MockLLMClient(response="test")
        agent = Agent(llm_client=mock_llm)

        response = 'Here is a tool call:\n<invoke name="bash">\n<parameter name="command">ls -la</parameter>\n</invoke>'

        result = agent._parse_tool_call(response)

        assert result is not None
        assert result["name"] == "bash"
        assert result["args"]["command"] == "ls -la"

    def test_parse_tool_call_no_match(self):
        mock_llm = MockLLMClient(response="test")
        agent = Agent(llm_client=mock_llm)

        response = "Just a regular response without tools"

        result = agent._parse_tool_call(response)

        assert result is None

    def test_parse_tool_call_multiple_params(self):
        mock_llm = MockLLMClient(response="test")
        agent = Agent(llm_client=mock_llm)

        response = (
            '<invoke name="web_search">\n<parameter name="query">python</parameter>\n</invoke>'
        )

        result = agent._parse_tool_call(response)

        assert result is not None
        assert result["name"] == "web_search"
        assert result["args"]["query"] == "python"


class TestExecuteTool:
    @pytest.mark.asyncio
    async def test_execute_tool_success(self):
        mock_llm = MockLLMClient(response="test")
        registry = ToolRegistry()

        class DummyTool:
            name = "dummy"
            description = "A dummy tool"

            async def execute(self, **kwargs) -> ToolResult:
                return ToolResult(success=True, result="executed")

        registry.register(DummyTool())
        agent = Agent(llm_client=mock_llm, tools=registry)

        result = await agent._execute_tool("dummy", {"arg1": "value"})

        assert result == "executed"

    @pytest.mark.asyncio
    async def test_execute_tool_not_found(self):
        mock_llm = MockLLMClient(response="test")
        registry = ToolRegistry()

        class DummyTool:
            name = "dummy"
            description = "A dummy tool"

            async def execute(self, **kwargs) -> ToolResult:
                return ToolResult(success=True, result="executed")

        registry.register(DummyTool())
        agent = Agent(llm_client=mock_llm, tools=registry)

        result = await agent._execute_tool("nonexistent", {})

        assert "not found" in result

    @pytest.mark.asyncio
    async def test_execute_tool_error(self):
        mock_llm = MockLLMClient(response="test")
        registry = ToolRegistry()

        class DummyTool:
            name = "dummy"
            description = "A dummy tool"

            async def execute(self, **kwargs) -> ToolResult:
                return ToolResult(success=False, result=None, error="Something went wrong")

        registry.register(DummyTool())
        agent = Agent(llm_client=mock_llm, tools=registry)

        result = await agent._execute_tool("dummy", {})

        assert "Error:" in result


class TestWebSearchTool:
    @pytest.mark.asyncio
    async def test_web_search_success(self):
        tool = WebSearchTool()

        with patch("src.tools.web_search.DDGS") as mock_ddgs:
            mock_instance = MagicMock()
            mock_instance.text.return_value = [
                {
                    "title": "Python",
                    "url": "https://python.org",
                    "body": "Python programming language",
                }
            ]
            mock_ddgs.return_value = mock_instance

            result = await tool.execute("python")

            assert result.success is True
            assert "Python" in result.result

    @pytest.mark.asyncio
    async def test_web_search_no_results(self):
        tool = WebSearchTool()

        with patch("src.tools.web_search.DDGS") as mock_ddgs:
            mock_instance = MagicMock()
            mock_instance.text.return_value = []
            mock_ddgs.return_value = mock_instance

            result = await tool.execute("nonexistent query")

            assert result.success is True
            assert "No search results" in result.result

    @pytest.mark.asyncio
    async def test_web_search_error(self):
        tool = WebSearchTool()

        with patch("src.tools.web_search.DDGS") as mock_ddgs:
            mock_instance = MagicMock()
            mock_instance.text.side_effect = Exception("Network error")
            mock_ddgs.return_value = mock_instance

            result = await tool.execute("test")

            assert result.success is False
            assert "Network error" in result.error
