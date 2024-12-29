from telegram import Update
from telegram.ext import (
    ContextTypes,
)

from src.telegram_bot import TelegramBot


class TelegramCallHandler:
    def __init__(self):
        self.telegram_bot = TelegramBot()

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Parses the CallbackQuery and updates the message text."""
        query = update.callback_query

        # CallbackQueries need to be answered, even if no notification to the user is needed
        # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
        await query.answer()
        await self.telegram_bot.set_message_reaction(query.message.message_id, query.data)

