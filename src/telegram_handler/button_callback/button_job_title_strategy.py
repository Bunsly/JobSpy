from typing import Union

from scrapers import JobPost
from telegram_bot import TelegramBot
from telegram_handler.button_callback.button_strategy import ButtonStrategy


class JobTitleStrategy(ButtonStrategy):
    def __init__(self, chat_id: Union[int, str], job: JobPost) -> None:
        """
        Usually, the Context accepts a strategy through the constructor, but
        also provides a setter to change it at runtime.
        """
        self._job = job
        self._chat_id = chat_id
        self.telegram_bot = TelegramBot()

    async def execute(self):
        await self.telegram_bot.send_job(self._chat_id, self._job)
