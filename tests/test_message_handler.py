"""Tests for the message handler module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agent import Agent
from src.llm import LLMError
from src.message_handler import create_handlers


class MockLLMClient:
    async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        return "AI response"


class TestMessageHandler:
    @pytest.fixture
    def agent(self):
        return Agent(llm_client=MockLLMClient())

    @pytest.mark.asyncio
    async def test_start_sends_greeting(self, agent):
        start, _, _ = create_handlers(agent)

        mock_message = MagicMock()
        mock_message.reply_text = AsyncMock()
        mock_update = MagicMock()
        mock_update.message = mock_message

        await start(mock_update, MagicMock())

        mock_message.reply_text.assert_called_once_with("Hello! I'm your panda assistant.")

    @pytest.mark.asyncio
    async def test_chat_sends_ai_response(self, agent):
        _, chat, _ = create_handlers(agent)

        mock_message = MagicMock()
        mock_message.text = "Hello"
        mock_message.reply_text = AsyncMock()
        mock_message.chat.send_action = AsyncMock()
        mock_update = MagicMock()
        mock_update.message = mock_message

        await chat(mock_update, MagicMock())

        mock_message.reply_text.assert_called_once_with("AI response")

    @pytest.mark.asyncio
    async def test_chat_handles_llm_error(self, agent):
        failing_agent = Agent(llm_client=MockLLMFailingClient())
        _, chat, _ = create_handlers(failing_agent)

        mock_message = MagicMock()
        mock_message.text = "Hello"
        mock_message.reply_text = AsyncMock()
        mock_message.chat.send_action = AsyncMock()
        mock_update = MagicMock()
        mock_update.message = mock_message

        await chat(mock_update, MagicMock())

        mock_message.reply_text.assert_called_once()
        args = mock_message.reply_text.call_args[0][0]
        assert "AI service" in args or "error" in args.lower()

    @pytest.mark.asyncio
    async def test_chat_ignores_empty_message(self, agent):
        _, chat, _ = create_handlers(agent)

        mock_update = MagicMock()
        mock_update.message = None

        await chat(mock_update, MagicMock())

    @pytest.mark.asyncio
    async def test_error_handler_logs_exception(self, agent):
        _, _, error = create_handlers(agent)

        mock_context = MagicMock()
        mock_context.error = ValueError("Test error")

        with patch("src.message_handler.logger") as mock_logger:
            await error(MagicMock(), mock_context)
            mock_logger.exception.assert_called_once()


class MockLLMFailingClient:
    async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        raise LLMError("Connection failed")
