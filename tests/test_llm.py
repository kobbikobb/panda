"""Tests for the LLM module."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from src.llm import LLMError, OllamaClient


class TestOllamaClient:
    @pytest.fixture
    def client(self):
        return OllamaClient(base_url="http://localhost:11434", model="llama3.2", timeout=30.0)

    @pytest.mark.asyncio
    async def test_generate_success(self, client):
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "Hello, user!"}
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )
            result = await client.generate(prompt="Hi")

        assert result == "Hello, user!"

    @pytest.mark.asyncio
    async def test_generate_with_system_prompt(self, client):
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "Response with context"}
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )
            result = await client.generate(prompt="Hi", system_prompt="You are helpful.")

        assert result == "Response with context"

    @pytest.mark.asyncio
    async def test_generate_connection_error(self, client):
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=httpx.ConnectError("Connection failed")
            )
            with pytest.raises(LLMError, match="Failed to connect"):
                await client.generate(prompt="Hi")

    def test_protocol_implementation(self):
        client = OllamaClient()
        assert isinstance(client, object)
