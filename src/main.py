"""Main entry point for the Panda Telegram bot."""

import logging
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from src.agent import Agent
from src.config import get_system_prompt
from src.llm import OllamaClient
from src.memory import SQLiteMemory
from src.message_handler import create_handlers
from src.tool_registry import ToolRegistry
from src.tools.web_search import WebSearchTool

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

load_dotenv()


def _get_token() -> str:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if token is None:
        raise ValueError("TELEGRAM_BOT_TOKEN not found in environment")
    return token


def main() -> None:
    llm_client = OllamaClient()
    memory = SQLiteMemory(max_messages=20)
    tools = ToolRegistry()
    tools.register(WebSearchTool())

    agent = Agent(
        llm_client=llm_client,
        memory=memory,
        tools=tools,
        system_prompt=get_system_prompt("default"),
    )
    start, chat, error = create_handlers(agent)

    app = Application.builder().token(_get_token()).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    app.add_error_handler(error)

    logger.info("Bot is starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
