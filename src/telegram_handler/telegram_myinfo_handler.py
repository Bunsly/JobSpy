from telegram import Update
from telegram.constants import ReactionEmoji
from telegram.ext import (
    ContextTypes,
)

from scrapers.utils import create_logger
from model.user_repository import user_repository
from telegram_bot import TelegramBot
from telegram_handler.telegram_handler import TelegramHandler


class MyInfoTelegramHandler(TelegramHandler):
    def __init__(self):
        self.telegram_bot = TelegramBot()
        self._logger = create_logger("MyInfoTelegramHandler")

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self._logger.info("start handling")
        chat_id = update.message.chat.id
        await self.telegram_bot.set_message_reaction(chat_id,
                                                     update.message.message_id, ReactionEmoji.FIRE)
        user = user_repository.find_by_username(update.message.from_user.username)
        await self.telegram_bot.send_text(chat_id, user.get_myinfo_message())

        self._logger.info("finished handling")


my_info_handler = MyInfoTelegramHandler()
