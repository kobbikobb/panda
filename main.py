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

load_dotenv()


def _get_token() -> str:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if token is None:
        raise ValueError("TELEGRAM_BOT_TOKEN not found in environment")
    return token


TOKEN = _get_token()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    await update.message.reply_text("Hello! I'm your panda assistant.")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    await update.message.reply_text(
        "Hey there, you are wonderful. I am not ready yet. Give me some time :)"
    )


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
