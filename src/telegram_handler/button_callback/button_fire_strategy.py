from telegram import MaybeInaccessibleMessage
from telegram.constants import ReactionEmoji

from db.job_repository import JobRepository
from jobspy import create_logger
from telegram_bot import TelegramBot
from telegram_handler.button_callback.button_strategy import ButtonStrategy


def _extract_job_id(message: str) -> str:
    """
    Extracts the job ID from a job description string.

    Args:
        message: The string containing the job description.

    Returns:
        The extracted job ID, or an empty string if not found.
    """
    # Find the starting position of the ID
    start_pos = message.find("Job ID: ")
    if start_pos == -1:
        return ""  # Not found

    # Find the ending position of the ID (excluding newline)
    end_pos = message.find("\n", start_pos + len("Job ID: "))
    if end_pos == -1:
        end_pos = len(message)  # No newline, use string end

    # Extract the ID substring
    return message[start_pos + len("Job ID: "):end_pos]


class FireStrategy(ButtonStrategy):
    def __init__(self, message: MaybeInaccessibleMessage) -> None:
        """
        Usually, the Context accepts a strategy through the constructor, but
        also provides a setter to change it at runtime.
        """
        self._message = message
        self._emoji = ReactionEmoji.FIRE
        self._telegram_bot = TelegramBot()
        self._job_repository = JobRepository()
        self._logger = create_logger("FireStrategy")

    async def execute(self):
        job_id = _extract_job_id(self._message.text)
        job = self._job_repository.find_by_id(job_id)
        if not job:
            self._logger.error(f"Job with ID {job_id} not found.")
            return
        job["applied"] = True
        self._job_repository.update(job)
        await self._telegram_bot.set_message_reaction(self._message.message_id, self._emoji)
