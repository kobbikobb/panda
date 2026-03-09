"""Telegram message handlers."""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from src.agent import Agent
from src.llm import LLMError

logger = logging.getLogger(__name__)


def create_handlers(agent: Agent) -> tuple[callable, callable, callable]:
    """Create handler functions with injected agent.

    Args:
        agent: The agent instance to use for processing messages.

    Returns:
        Tuple of (start_handler, chat_handler, error_handler).
    """

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.message is None:
            return
        await update.message.reply_text("Hello! I'm your panda assistant.")

    async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.message is None:
            return
        user_message = update.message.text
        if user_message is None:
            return

        await update.message.chat.send_action("typing")

        try:
            response = await agent.process(user_message)
            await update.message.reply_text(response)
        except LLMError as e:
            logger.error(f"LLM error: {e}")
            await update.message.reply_text(
                "Sorry, I'm having trouble connecting to the AI service. Please try again later."
            )
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            await update.message.reply_text("Sorry, I encountered an unexpected error.")

    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.exception("Exception while handling update:", exc_info=context.error)

    return start, chat, error_handler
