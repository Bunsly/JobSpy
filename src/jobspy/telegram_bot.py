import os
from dotenv import load_dotenv
from telegram import Bot

from jobspy.jobs import JobPost

load_dotenv()


class TelegramBot:

    def __init__(self):
        self._api_token = os.getenv("TELEGRAM_API_TOKEN")
        self.chatId = os.getenv("TELEGRAM_CHAT_ID")
        self.bot = Bot(token=self._api_token)

    async def send_job(self, job: JobPost):
        """
        Send JobPost details to Telegram chat.
        """
        message = f"New Job Posted:\n\n" \
            f"Job ID: {job.id}\n" \
            f"Job Title: {job.title}\n" \
            f"Company: {job.company_name}\n" \
            f"Location: {job.location}\n" \
            f"Link: {job.job_url}\n"
        try:
            await self.bot.sendMessage(chat_id=self.chatId, text=message)
            print(f"Sent job to Telegram: {job.id}")
        except Exception as e:
            print(f"Failed to send job to Telegram: {e}")
