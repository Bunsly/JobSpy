from enum import Enum

from telegram import Update, Chat, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.constants import ReactionEmoji
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters,
)

from config.cache_manager import cache_manager
from model.Position import Position
from model.User import User
from model.user_repository import user_repository
from scrapers.utils import create_logger
from telegram_bot import TelegramBot
from telegram_handler.start_handler_constats import START_MESSAGE, POSITION_MESSAGE, POSITION_NOT_FOUND, \
    LOCATION_MESSAGE, EXPERIENCE_MESSAGE, FILTER_TILE_MESSAGE, THANK_YOU_MESSAGE, BYE_MESSAGE, VERIFY_MESSAGE, \
    SEARCH_MESSAGE, EXPERIENCE_INVALID, JOB_AGE_INVALID, JOB_AGE_MESSAGE


class Flow(Enum):
    POSITION = 0
    ADDRESS = 1
    FILTERS = 2
    EXPERIENCE = 3
    VERIFY_ADDRESS = 4
    VERIFY_FILTERS = 5
    SKIP_FILTERS = 6
    JOB_AGE = 7


class TelegramStartHandler:

    def __init__(self):
        self.telegram_bot = TelegramBot()
        self.logger = create_logger("TelegramStartHandler")

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Starts the conversation and asks the user about their position."""
        chat: Chat = update.message.chat
        user = user_repository.find_by_username(chat.username)
        if not user:
            user = User(full_name=chat.full_name, username=chat.username, chat_id=chat.id)
            user_repository.insert_user(user)

        await update.message.reply_text(START_MESSAGE)

        buttons = [[KeyboardButton(position.value)] for position in Position]
        reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True,
                                           input_field_placeholder=Flow.POSITION.name)
        await update.message.reply_text(
            POSITION_MESSAGE,
            reply_markup=reply_markup,
        )

        return Flow.POSITION.value

    async def position(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Stores the selected position and asks for a locations."""
        user = update.message.from_user
        self.logger.info("Position of %s: %s", user.first_name, update.message.text)
        position = next((p for p in Position if p.value == update.message.text), None)
        if not position:
            await update.message.set_reaction(ReactionEmoji.PILE_OF_POO)
            await update.message.reply_text(POSITION_NOT_FOUND)
            buttons = [[KeyboardButton(position.value)] for position in Position]
            reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True,
                                               input_field_placeholder=Flow.POSITION.name)
            await update.message.reply_text(
                POSITION_MESSAGE,
                reply_markup=reply_markup,
            )
            return Flow.POSITION.value

        await update.message.set_reaction(ReactionEmoji.FIRE)
        cached_user: User = cache_manager.find(user.username)
        cached_user.position = position
        cache_manager.save(cached_user.username, cached_user)
        await update.message.reply_text(LOCATION_MESSAGE)

        return Flow.ADDRESS.value

    async def address(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Asks for a location."""
        cities = update.message.text.split(",")
        # Remove leading/trailing spaces from each city name
        cities = [city.strip() for city in cities]
        await update.message.set_reaction(ReactionEmoji.FIRE)
        reply_markup = ReplyKeyboardMarkup([[KeyboardButton("Yes"), KeyboardButton("No")]], one_time_keyboard=True,
                                           input_field_placeholder=Flow.VERIFY_ADDRESS.name)
        await update.message.reply_text(VERIFY_MESSAGE % cities, reply_markup=reply_markup)

        cached_user: User = cache_manager.find(update.message.from_user.username)
        cached_user.cities = cities
        cache_manager.save(cached_user.username, cached_user)

        return Flow.VERIFY_ADDRESS.value

    async def verify_address(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Verify for a Address."""
        if update.message.text == "No":
            await update.message.set_reaction(ReactionEmoji.PILE_OF_POO)
            await update.message.reply_text(LOCATION_MESSAGE)
            return Flow.ADDRESS.value

        await update.message.set_reaction(ReactionEmoji.FIRE)
        await update.message.reply_text(EXPERIENCE_MESSAGE)

        return Flow.EXPERIENCE.value

    async def experience(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Asks for a experience."""
        user = update.message.from_user
        self.logger.info("Experience of %s: %s", user.first_name, update.message.text)

        if not update.message.text.isnumeric():
            await update.message.set_reaction(ReactionEmoji.PILE_OF_POO)
            await update.message.reply_text(EXPERIENCE_INVALID)
            await update.message.reply_text(EXPERIENCE_MESSAGE)

            return Flow.EXPERIENCE.value

        await update.message.set_reaction(ReactionEmoji.FIRE)
        cached_user: User = cache_manager.find(update.message.from_user.username)
        cached_user.experience = update.message.text
        cache_manager.save(cached_user.username, cached_user)
        await update.message.reply_text(JOB_AGE_MESSAGE)
        return Flow.JOB_AGE.value

    async def job_age(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Asks for a Job age in hours."""
        await update.message.set_reaction(ReactionEmoji.FIRE)
        user = update.message.from_user
        self.logger.info("Job age of %s: %s", user.first_name, update.message.text)

        if not update.message.text.isnumeric():
            await update.message.set_reaction(ReactionEmoji.PILE_OF_POO)
            await update.message.reply_text(JOB_AGE_INVALID)
            await update.message.reply_text(JOB_AGE_MESSAGE)

            return Flow.JOB_AGE.value
        await update.message.set_reaction(ReactionEmoji.FIRE)
        cached_user: User = cache_manager.find(update.message.from_user.username)
        cached_user.job_age = update.message.text
        cache_manager.save(cached_user.username, cached_user)
        await update.message.reply_text(
            FILTER_TILE_MESSAGE)

        return Flow.FILTERS.value

    async def filters_flow(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Asks for a filters_flow."""
        await update.message.set_reaction(ReactionEmoji.FIRE)
        title_filters = update.message.text.split(",")
        # Remove leading/trailing spaces from each city name
        title_filters = [title_filter.strip() for title_filter in title_filters]
        reply_markup = ReplyKeyboardMarkup([[KeyboardButton("Yes"), KeyboardButton("No")]], one_time_keyboard=True,
                                           input_field_placeholder=Flow.VERIFY_FILTERS.name)
        await update.message.reply_text(VERIFY_MESSAGE % title_filters, reply_markup=reply_markup)

        cached_user: User = cache_manager.find(update.message.from_user.username)
        cached_user.title_filters = title_filters
        cache_manager.save(cached_user.username, cached_user)

        return Flow.VERIFY_FILTERS.value

    async def verify_filter(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Verify for a filters_flow."""
        if update.message.text == "No":
            await update.message.set_reaction(ReactionEmoji.PILE_OF_POO)
            await update.message.reply_text(FILTER_TILE_MESSAGE)
            return Flow.FILTERS.value

        await update.message.set_reaction(ReactionEmoji.FIRE)
        await update.message.reply_text(THANK_YOU_MESSAGE)
        await update.message.reply_text(SEARCH_MESSAGE)
        cached_user: User = cache_manager.find(update.message.from_user.username)
        user_repository.update(cached_user)
        return ConversationHandler.END

    async def skip_filter(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Skips the location and asks for info about the user."""
        await update.message.set_reaction(ReactionEmoji.FIRE)
        user = update.message.from_user
        self.logger.info("User %s did not send a filters.", user.first_name)
        await update.message.reply_text(THANK_YOU_MESSAGE)
        await update.message.reply_text(SEARCH_MESSAGE)

        return ConversationHandler.END

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancels and ends the conversation."""
        await update.message.set_reaction(ReactionEmoji.FIRE)
        user = update.message.from_user
        self.logger.info("User %s canceled the conversation.", user.first_name)
        await update.message.reply_text(
            BYE_MESSAGE, reply_markup=ReplyKeyboardRemove()
        )
        cached_user: User = cache_manager.find(user.username)
        user_repository.update(cached_user.username, cached_user)
        return ConversationHandler.END


start_handler = TelegramStartHandler()
start_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start_handler.start)],
    states={
        Flow.POSITION.value: [MessageHandler(filters.TEXT, start_handler.position)],
        Flow.ADDRESS.value: [MessageHandler(filters.TEXT, start_handler.address)],
        Flow.VERIFY_ADDRESS.value: [MessageHandler(filters.TEXT, start_handler.verify_address)],
        Flow.EXPERIENCE.value: [MessageHandler(filters.TEXT, start_handler.experience)],
        Flow.JOB_AGE.value: [MessageHandler(filters.TEXT, start_handler.job_age)],
        Flow.FILTERS.value: [MessageHandler(filters.TEXT, start_handler.filters_flow)],
        Flow.VERIFY_FILTERS.value: [MessageHandler(filters.TEXT, start_handler.verify_filter)],
    },
    fallbacks=[CommandHandler("cancel", start_handler.cancel)],
)
