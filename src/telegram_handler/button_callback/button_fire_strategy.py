from telegram import MaybeInaccessibleMessage
from telegram.constants import ReactionEmoji

from src.telegram_bot import TelegramBot
from src.telegram_handler.button_callback.button_strategy import ButtonStrategy


class FireStrategy(ButtonStrategy):
    def __init__(self, data: MaybeInaccessibleMessage) -> None:
        """
        Usually, the Context accepts a strategy through the constructor, but
        also provides a setter to change it at runtime.
        """
        self.data = data
        self._emoji = ReactionEmoji.FIRE

    async def execute(self):
        telegram_bot = TelegramBot()
        await telegram_bot.set_message_reaction(self.data.message_id, self._emoji)
        # find the position in DB
        # set applied to True
        # save
        # set reaction to message
        pass
