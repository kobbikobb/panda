# Panda

A Telegram bot powered by an LLM agent.

## What is Panda?

Panda is a personal AI assistant that you can interact with through Telegram. It can answer questions, help with tasks, and eventually read your emails.

## Interacting with Panda

1. Open Telegram and search for **@panda_1337_bot**
2. Send `/start` to begin
3. Send any message to chat with Panda

Panda uses Ollama (llama3.2) to generate responses!

## Quick Start (Docker Compose)

```bash
# Clone the repo and start everything
cp .env.example .env  # Edit .env with your TELEGRAM_BOT_TOKEN
docker compose up -d --build

# View logs
docker compose logs -f
```

## Development

### Prerequisites

- Docker & Docker Compose
- Colima (for macOS): `brew install colima`

### Running Locally

```bash
# Start colima (macOS)
colima start

# Install dependencies
uv sync

# Run locally (requires Ollama running separately)
uv run python main.py
```

### Running with Docker Compose

```bash
# Create environment file
cp .env.example .env
# Edit .env with TELEGRAM_BOT_TOKEN

# Start all services
docker compose up -d

# Pull the Ollama image and model
docker compose pull ollama
docker compose exec ollama ollama pull llama3.2

# View logs
docker compose logs -f

# Stop everything
docker compose down
```

### Running Tests

```bash
# Install dependencies and run tests
uv sync
uv run pytest

# Run linter
uv run ruff check
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token | Required |
| `OLLAMA_BASE_URL` | Ollama API URL | `http://localhost:11434` |

## Future Considerations

- **User data isolation**: Each user should only access their own data (e.g., their own emails)

## Phases

- Phase 1: Echo Bot ✅
- Phase 2: Dockerize ✅
- Phase 3: CI/CD Pipeline ✅
- Phase 4: Ollama Integration ✅
- Phase 5: Tool Architecture
- Phase 6: Email Integration
- Phase 7: Azure Deployment
