import asyncio

from dotenv import load_dotenv

from telegram_bot import TelegramBot
from tests.test_util import createMockJob

load_dotenv()


class TelegramTests:

    def __init__(self):
        """
        This block ensures that the script runs the test only when executed directly,
        not when imported as a module.
        """
        self.bot = TelegramBot()

    async def send_job(self):
        """
        Sents a mock job Telegram using Telegram Bot.
        """
        job = createMockJob()
        await self.bot.send_job(job)
        print(f"Test sent job finished.")


if __name__ == '__main__':
    # Create an instance of DatabaseTests
    tests = TelegramTests()

    # Run the send_job test
    asyncio.run(tests.send_job())
