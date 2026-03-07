# Panda

A Telegram bot powered by an LLM agent.

## What is Panda?

Panda is a personal AI assistant that you can interact with through Telegram. It can answer questions, help with tasks, and eventually read your emails.

## Interacting with Panda

1. Open Telegram and search for **@panda_1337_bot**
2. Send `/start` to begin
3. Send any message to chat with Panda

Currently Panda will respond with "sorry I am not ready yet answear" - more features coming soon!

## Development

### Setup

```bash
# Install dependencies
uv sync

# Run locally
uv run python main.py
```

### Environment Variables

Create a `.env` file with:
```
TELEGRAM_BOT_TOKEN=your_token_here
```

## Future Considerations

- **User data isolation**: Each user should only access their own data (e.g., their own emails)

## Phases

- Phase 1: Echo Bot ✅
- Phase 2: Dockerize
- Phase 3: CI/CD Pipeline
- Phase 4: Ollama Integration
- Phase 5: Tool Architecture
- Phase 6: Email Integration
- Phase 7: Azure Deployment
