import logging
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from ollama_client import OllamaClient, OllamaError

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


TOKEN = _get_token()

ollama = OllamaClient()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    await update.message.reply_text("Hello! I'm your panda assistant.")


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    user_message = update.message.text
    if user_message is None:
        return

    await update.message.chat.send_action("typing")

    try:
        response = await ollama.generate(
            prompt=user_message,
            system_prompt="You are a helpful AI assistant named Panda. Keep responses concise and friendly.",
        )
        await update.message.reply_text(response)
    except OllamaError as e:
        logger.error(f"Ollama error: {e}")
        await update.message.reply_text(
            "Sorry, I'm having trouble connecting to the AI service. Please try again later."
        )
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        await update.message.reply_text("Sorry, I encountered an unexpected error.")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.exception("Exception while handling update:", exc_info=context.error)


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    app.add_error_handler(error_handler)

    logger.info("Bot is starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
