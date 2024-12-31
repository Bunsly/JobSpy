from telegram import Update
from telegram.ext import (
    ContextTypes,
)

from jobspy import create_logger
from telegram_bot import TelegramBot
from telegram_handler.button_callback.button_callback_context import ButtonCallBackContext


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


class TelegramCallHandler:
    def __init__(self):
        self.telegram_bot = TelegramBot()
        self.logger = create_logger("TelegramCallHandler")

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Parses the CallbackQuery and updates the message."""
        query = update.callback_query
        await query.answer()
        job_id = _extract_job_id(query.message.text)
        button_context = ButtonCallBackContext(query.data, query.message, job_id)

        await button_context.run()
