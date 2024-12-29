from __future__ import annotations

from src.telegram_bot import TelegramBot
from src.telegram_handler.button_callback.button_strategy import ButtonStrategy


class ButtonCallBackContext():
    """
    The Context defines the interface
    """

    def __init__(self, strategy: ButtonStrategy = None) -> None:
        self.telegram_bot = TelegramBot()
        self._strategy = strategy

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
        #  extract job id from message
        # find the position in DB
        # set applied to True
        # save
        # set reaction to message

        print("Context: Starting")
        await self._strategy.execute()
        print("Context: Finished")

        # ...
