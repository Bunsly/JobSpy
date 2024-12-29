from telegram import Update
from telegram.constants import ReactionEmoji
from telegram.ext import (
    ContextTypes,
)

from src.telegram_bot import TelegramBot
from src.telegram_handler.button_callback.button_callback_context import ButtonCallBackContext
from src.telegram_handler.button_callback.button_fire_strategy import FireStrategy
from src.telegram_handler.button_callback.button_poo_strategy import PooStrategy


class TelegramCallHandler:
    def __init__(self):
        self.telegram_bot = TelegramBot()

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Parses the CallbackQuery and updates the message text."""
        query = update.callback_query

        # CallbackQueries need to be answered, even if no notification to the user is needed
        # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
        await query.answer()
        button_context = ButtonCallBackContext()
        if ReactionEmoji.FIRE.name == query.data:
            strategy = FireStrategy(query.message)
        # elif ReactionEmoji.PILE_OF_POO.name == query.data:
        #     strategy = PooStrategy(query.message)
        else:
            raise ValueError("Invalid enum value")

        if not strategy:
            return

        button_context.strategy = strategy
        await button_context.run()

