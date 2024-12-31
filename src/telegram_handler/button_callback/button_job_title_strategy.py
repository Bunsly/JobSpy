from jobspy import JobPost
from telegram_bot import TelegramBot
from telegram_handler.button_callback.button_strategy import ButtonStrategy


class JobTitleStrategy(ButtonStrategy):
    def __init__(self, job: JobPost) -> None:
        """
        Usually, the Context accepts a strategy through the constructor, but
        also provides a setter to change it at runtime.
        """
        self._job = job
        self.telegram_bot = TelegramBot()

    async def execute(self):
        await self.telegram_bot.send_job(self._job)
