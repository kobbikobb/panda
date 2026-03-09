"""LLM client abstraction and implementations."""

import os
from typing import Protocol, runtime_checkable

import httpx


class LLMError(Exception):
    """Base exception for LLM-related errors."""

    pass


@runtime_checkable
class LLMClient(Protocol):
    """Protocol defining the interface for LLM clients."""

    async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        """Generate a response from the LLM.

        Args:
            prompt: The user prompt.
            system_prompt: Optional system prompt to set context.

        Returns:
            The LLM's response as a string.

        Raises:
            LLMError: If the LLM call fails.
        """
        ...


class OllamaClient:
    """Async client for the Ollama API."""

    def __init__(
        self,
        base_url: str | None = None,
        model: str = "llama3.2",
        timeout: float = 120.0,
    ):
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = model
        self.timeout = timeout

    async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        payload: dict[str, str | bool] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                return data.get("response", "")
        except httpx.ConnectError as e:
            raise LLMError(f"Failed to connect to Ollama at {self.base_url}") from e
        except httpx.TimeoutException as e:
            raise LLMError(f"Request to Ollama timed out after {self.timeout}s") from e
        except httpx.HTTPStatusError as e:
            raise LLMError(
                f"Ollama returned error: {e.response.status_code} - {e.response.text}"
            ) from e
        except Exception as e:
            raise LLMError(f"Unexpected error calling Ollama: {e}") from e
