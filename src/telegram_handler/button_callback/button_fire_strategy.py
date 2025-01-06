from telegram import MaybeInaccessibleMessage
from telegram.constants import ReactionEmoji

from scrapers import create_logger
from model.job_repository import job_repository
from telegram_bot import TelegramBot
from telegram_handler.button_callback.button_strategy import ButtonStrategy


class FireStrategy(ButtonStrategy):
    def __init__(self, message: MaybeInaccessibleMessage, job_id: str) -> None:
        """
        Usually, the Context accepts a strategy through the constructor, but
        also provides a setter to change it at runtime.
        """
        self._message = message
        self._emoji = ReactionEmoji.FIRE
        self._telegram_bot = TelegramBot()
        self._job_id = job_id
        self._logger = create_logger("FireStrategy")

    async def execute(self):
        job = job_repository.find_by_id(self._job_id)
        if not job:
            self._logger.error(f"Job with ID {self._job_id} not found.")
            return
        job.applied = True
        job_repository.update(job)
        chat_id = self._message.chat.id
        await self._telegram_bot.set_message_reaction(chat_id, self._message.message_id, self._emoji)
