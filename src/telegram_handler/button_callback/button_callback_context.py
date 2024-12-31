from __future__ import annotations

from telegram import MaybeInaccessibleMessage
from telegram.constants import ReactionEmoji

from jobspy import create_logger
from telegram_bot import TelegramBot
from telegram_handler.button_callback.button_fire_strategy import FireStrategy
from telegram_handler.button_callback.button_poo_strategy import PooStrategy
from telegram_handler.button_callback.button_strategy import ButtonStrategy


class ButtonCallBackContext:
    """
    The Context defines the interface
    """

    def __init__(self, data: str, message: MaybeInaccessibleMessage,job_id:str) -> None:
        self._logger = create_logger("Button CallBack Context")
        self._message = message
        self._data = data
        self._telegram_bot = TelegramBot()
        self._job_id = job_id

    @property
    def strategy(self) -> ButtonStrategy:
        """
        The Context maintains a reference to one of the Strategy objects. The
        Context does not know the concrete class of a strategy. It should work
        with all strategies via the Strategy interface.
        """

        return self._strategy

    @strategy.setter
    def strategy(self, strategy: ButtonStrategy) -> None:
        """
        Usually, the Context allows replacing a Strategy object at runtime.
        """

        self._strategy = strategy

    async def run(self) -> None:
        self._logger.info("Starting")
        if ReactionEmoji.FIRE.name == self._data:
            self.strategy = FireStrategy(self._message,self._job_id)
        elif ReactionEmoji.PILE_OF_POO.name == self._data:
            self.strategy = PooStrategy(self._message)
        else:
            self._logger.error("Invalid enum value")
            return

        await self._strategy.execute()
        self._logger.info("Finished")
