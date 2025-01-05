from enum import Enum

from telegram import Update, Chat, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters,
)

from model.Position import Position
from model.User import User
from model.user_repository import UserRepository, user_repository
from jobspy.scrapers.utils import create_logger
from telegram_bot import TelegramBot
from telegram_handler.start_handler_constats import START_MESSAGE, POSITION_MESSAGE, POSITION_NOT_FOUND, \
    LOCATION_MESSAGE, EXPERIENCE_MESSAGE, FILTER_TILE_MESSAGE, THANK_YOU_MESSAGE, BYE_MESSAGE, VERIFY_MESSAGE
from telegram_handler.telegram_handler import TelegramHandler


class Flow(Enum):
    POSITION = 0
    ADDRESS = 1
    FILTERS = 2
    EXPERIENCE = 3
    VERIFY_ADDRESS = 4
    VERIFY_FILTERS = 5
    SKIP_FILTERS = 6


class TelegramStartHandler(TelegramHandler):

    def __init__(self):
        self.filters = None
        self.telegram_bot = TelegramBot()
        self.logger = create_logger("TelegramStartHandler")
        self.temp_user = None
        self.cities = None

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Starts the conversation and asks the user about their position."""
        chat: Chat = update.message.chat
        user = User(full_name=chat.full_name, username=chat.username, chat_id=chat.id)
        # user_repository.insert_user(user)
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
        position = next((p for p in Position if p.name == update.message.text), None)
        if not position:
            await update.message.reply_text(POSITION_NOT_FOUND)
            buttons = [[KeyboardButton(position.name)] for position in Position]
            reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True,
                                               input_field_placeholder=Flow.POSITION.name)
            await update.message.reply_text(
                POSITION_MESSAGE,
                reply_markup=reply_markup,
            )
            return Flow.POSITION.value

        await update.message.reply_text(LOCATION_MESSAGE)

        return Flow.ADDRESS.value

    async def address(self, update: Update) -> int:
        """Asks for a location."""
        user = update.message.from_user
        self.cities = update.message.text.split(",")
        reply_markup = ReplyKeyboardMarkup([[KeyboardButton("Yes"), KeyboardButton("No")]], one_time_keyboard=True,
                                           input_field_placeholder=Flow.VERIFY_ADDRESS.name)
        await update.message.reply_text(VERIFY_MESSAGE % self.filters, reply_markup=reply_markup)

        return Flow.VERIFY_ADDRESS.value

    async def verify_address(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Verify for a Address."""
        if update.message.text == "No":
            await update.message.reply_text(LOCATION_MESSAGE)
            return Flow.ADDRESS.value

        reply_markup = ReplyKeyboardMarkup([["1", "2"]], one_time_keyboard=True,
                                           input_field_placeholder=Flow.VERIFY_ADDRESS.name)
        await update.message.reply_text(EXPERIENCE_MESSAGE,
                                        reply_markup=reply_markup
                                        )

        return Flow.EXPERIENCE.value

    async def experience(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Asks for a experience."""
        user = update.message.from_user
        self.logger.info("Experience of %s: %s", user.first_name, update.message.text)

        await update.message.reply_text(
            FILTER_TILE_MESSAGE)
        return Flow.FILTERS.value

    async def filters_flow(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Asks for a filters_flow."""
        self.filters = update.message.text.split(",")
        reply_markup = ReplyKeyboardMarkup([[KeyboardButton("Yes"), KeyboardButton("No")]], one_time_keyboard=True,
                                           input_field_placeholder=Flow.VERIFY_FILTERS.name)
        await update.message.reply_text(VERIFY_MESSAGE % self.filters, reply_markup=reply_markup)

        return Flow.VERIFY_FILTERS.value

    async def verify_filter(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Verify for a filters_flow."""
        if update.message.text == "No":
            await update.message.reply_text(FILTER_TILE_MESSAGE)
            return Flow.FILTERS.value

        await update.message.reply_text(THANK_YOU_MESSAGE)

        return ConversationHandler.END

    async def skip_filter(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Skips the location and asks for info about the user."""
        user = update.message.from_user
        self.logger.info("User %s did not send a filters.", user.first_name)
        await update.message.reply_text(THANK_YOU_MESSAGE)

        return ConversationHandler.END

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancels and ends the conversation."""
        user = update.message.from_user
        self.logger.info("User %s canceled the conversation.", user.first_name)
        await update.message.reply_text(
            BYE_MESSAGE, reply_markup=ReplyKeyboardRemove()
        )

        return ConversationHandler.END

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.logger.info("start handling")
        # chat: Chat = update.message.chat
        # chat.id - 368620919
        # chat.username - 'Qw1zeR'
        # chat.full_name - 'Qw1zeR'
        # user = User(full_name=chat.full_name, username=chat.username, chat_id=chat.id)
        # user_repository.insert_user(user)
        # fields = field_repository.find_all()  # Get all fields from the database
        # buttons = [[KeyboardButton(field.name)] for field in fields]
        # reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True)
        #
        # await update.message.reply_text("Please select your field:", reply_markup=reply_markup)
        # await self.telegram_bot.set_message_reaction(
        #     update.message.message_id, ReactionEmoji.FIRE)
        # site_names = [site.name for site in self.sites_to_scrap]
        # site_names_print = ", ".join(site_names)
        # await self.telegram_bot.send_text(
        #     f"Start scarping: {site_names_print}")
        # self.logger.info(f"Found {len(jobs)} jobs")
        # self.jobRepository.insert_many_if_not_found(filtered_out_jobs)
        # old_jobs, new_jobs = self.jobRepository.insert_many_if_not_found(jobs)
        # for newJob in new_jobs:
        #     await self.telegram_bot.send_job(newJob)
        # self.logger.info(f"Found {len(old_jobs)} old jobs")
        # await self.telegram_bot.send_text(
        #     f"Finished scarping: {site_names_print}")
        self.logger.info("finished handling")


start_handler = TelegramStartHandler()
start_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start_handler.start)],
    states={
        Flow.POSITION.value: [MessageHandler(filters.TEXT, start_handler.position)],
        Flow.ADDRESS.value: [MessageHandler(filters.TEXT, start_handler.address)],
        Flow.VERIFY_ADDRESS.value: [MessageHandler(filters.TEXT, start_handler.verify_address)],
        Flow.EXPERIENCE.value: [MessageHandler(filters.TEXT, start_handler.experience)],
        Flow.FILTERS.value: [MessageHandler(filters.TEXT, start_handler.filters_flow)],
        Flow.VERIFY_FILTERS.value: [MessageHandler(filters.TEXT, start_handler.verify_filter)],
    },
    fallbacks=[CommandHandler("cancel", start_handler.cancel)],
)
