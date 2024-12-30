from telegram import MaybeInaccessibleMessage
from telegram.constants import ReactionEmoji

from telegram_handler.button_callback.button_strategy import ButtonStrategy


class PooStrategy(ButtonStrategy):
    def __init__(self, data: MaybeInaccessibleMessage) -> None:
        """
        Usually, the Context accepts a strategy through the constructor, but
        also provides a setter to change it at runtime.
        """
        self.data = data
        self._emoji = ReactionEmoji.PILE_OF_POO

    async def execute(self):
        pass
