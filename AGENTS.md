# AGENTS.md - Guidelines for Agentic Coding

This file provides guidelines for agents operating in this repository.

## Project Overview

Panda is a Telegram bot with LLM integration. It uses `python-telegram-bot` for Telegram interaction and connects to Ollama for LLM capabilities.

## Commands

### Install Dependencies
```bash
uv sync
```

### Lint
```bash
uv run ruff check .
```

### Fix Lint Issues
```bash
uv run ruff check . --fix
```

### Test
```bash
uv run pytest
```

### Run Single Test
```bash
uv run pytest tests/test_agent.py::TestAgent::test_process_returns_llm_response
uv run pytest tests/test_llm.py -v
```

### Run Application
```bash
python -m src.main
```

## Code Style Guidelines

### General Principles

- **Lean comments**: Keep comments brief and purposeful. Code should speak for itself.
- **Constructor injection**: Always use constructor injection for dependencies. Never hardcode dependencies inside classes.
- **Protocols for interfaces**: Use `typing.Protocol` to define interfaces for dependency injection and testability.

### Imports

- Use `ruff` import sorting (stdlib first, then third-party, then local)
- Sort imports alphabetically within each group
- Example:
  ```python
  from unittest.mock import AsyncMock, MagicMock

  import pytest

  from src.agent import Agent
  from src.llm import LLMError
  ```

### Formatting

- Line length: 100 characters max
- Use 4 spaces for indentation (no tabs)
- One blank line between top-level definitions
- No trailing whitespace

### Types

- Use Python 3.14+ native union syntax: `str | None` instead of `Optional[str]`
- Use type hints for all function parameters and return values
- Use `object` for Telegram update/context types when exact type is uncertain
- Private attributes should be prefixed with `_`

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `OllamaClient`, `Agent`)
- **Functions/methods**: `snake_case` (e.g., `create_handlers`, `process`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`)
- **Private members**: `_leading_underscore` (e.g., `_llm_client`)

### Error Handling

- Use custom exception classes for domain-specific errors
- Catch specific exceptions, not bare `Exception`
- Log errors with appropriate level before re-raising or responding
- Never expose internal error details to external users

### Dependency Injection Pattern

Always inject dependencies via constructor:

```python
class Agent:
    def __init__(self, llm_client: LLMClient, system_prompt: str | None = None):
        self._llm_client = llm_client
        self._system_prompt = system_prompt
```

This makes the class testable - pass a mock in tests.

### Protocol Example

Define interfaces with `Protocol` for swapability:

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class LLMClient(Protocol):
    async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        ...
```

### Async/Await

- Use `async def` for asynchronous functions
- Always `await` async calls
- Use `pytest-asyncio` for async tests with `@pytest.mark.asyncio`

### Testing

- Mock external dependencies (LLM clients, HTTP calls)
- Test both success and error paths
- Use `AsyncMock` for async methods
- Keep tests focused and named descriptively

### Module Structure

```
src/
├── __init__.py       # Package marker
├── main.py           # Entry point
├── agent.py          # Business logic
├── llm.py            # LLM abstractions and implementations
└── message_handler.py  # Telegram handlers
```

### Running the Bot

1. Create `.env` file (copy from `.env.example`):
   ```
   TELEGRAM_BOT_TOKEN=your_token_here
   OLLAMA_BASE_URL=http://localhost:11434
   ```

2. Start Ollama locally or via Docker

3. Run the bot:
   ```bash
   python -m src.main
   ```

### Docker

```bash
docker compose up --build
```

This starts both Ollama and the bot container.
