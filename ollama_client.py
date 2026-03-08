import os

import httpx


class OllamaClient:
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

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
