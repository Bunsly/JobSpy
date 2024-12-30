from telegram import MaybeInaccessibleMessage
from telegram.constants import ReactionEmoji

from telegram_bot import TelegramBot
from telegram_handler.button_callback.button_strategy import ButtonStrategy


class PooStrategy(ButtonStrategy):
    def __init__(self, message: MaybeInaccessibleMessage) -> None:
        """
        Usually, the Context accepts a strategy through the constructor, but
        also provides a setter to change it at runtime.
        """
        self.message = message
        self._emoji = ReactionEmoji.PILE_OF_POO
        self.telegram_bot = TelegramBot()

    async def execute(self):
        await self.telegram_bot.set_message_reaction(self.message.message_id, self._emoji)

