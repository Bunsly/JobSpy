import os
from dotenv import load_dotenv
from telegram import Bot, Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from .scrapers.utils import create_logger

load_dotenv()

logger = create_logger("TelegramBot")


class TelegramHandler:
    def __init__(self):
        self._api_token = os.getenv("TELEGRAM_API_TOKEN")
        self.chatId = os.getenv("TELEGRAM_CHAT_ID")
        self.bot = Bot(token=self._api_token)
        # Create the Application and pass it your bot's token.
        self.application = Application.builder().token(self._api_token).build()

    async def findAll(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start the conversation and ask user for input."""
        await update.message.reply_text(
            "Hi! My name is Doctor Botter. I will hold a more complex conversation with you. "
            "Why don't you tell me something about yourself?"
        )

    async def find_glassdoor(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start the conversation and ask user for input."""
        await update.message.reply_text(
            "Hi! My name is Doctor Botter. I will hold a more complex conversation with you. "
            "Why don't you tell me something about yourself?"
        )

    def handler(self):
        self.application.add_handler(CommandHandler("find", self.findAll))
        self.application.add_handler(CommandHandler("galssdoor", self.find_glassdoor))
        self.application.add_handler(CommandHandler("linkedin", self.findAll))
        self.application.add_handler(CommandHandler("indeed", self.findAll))
        self.application.add_handler(CommandHandler("goozali", self.findAll))
        # Run the bot until the user presses Ctrl-C
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)