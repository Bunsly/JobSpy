from enum import Enum

from telegram import Update, Chat, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters,
)

from db.User import User
from db.position_repository import position_repository
from db.user_repository import UserRepository
from jobspy.scrapers.utils import create_logger
from telegram_bot import TelegramBot
from telegram_handler.telegram_handler import TelegramHandler


class Flow(Enum):
    POSITION = 0
    ADDRESS = 1
    FILTERS = 2
    EXPERIENCE = 3
    RETRY = 4


class TelegramStartHandler(TelegramHandler):

    def __init__(self):
        self.telegram_bot = TelegramBot()
        self.user_repository = UserRepository()
        self.logger = create_logger("TelegramStartHandler")
        self.positions = position_repository.find_all()
        self.temp_user = None
        self.last_state = None

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Flow:
        """Starts the conversation and asks the user about their position."""
        chat: Chat = update.message.chat
        user = User(full_name=chat.full_name, username=chat.username, chat_id=chat.id)
        self.user_repository.insert_user(user)

        buttons = [[KeyboardButton(position.name)] for position in self.positions]
        reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True,
                                           input_field_placeholder=Flow.POSITION.name)
        await update.message.reply_text(
            "Hi! My name is Professor Bot. I will hold a conversation with you. "
            "Send /cancel to stop talking to me.\n\n"
            "What Position are you looking for?",
            reply_markup=reply_markup,
        )

        return Flow.POSITION

    async def position(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Flow:
        """Stores the selected position and asks for a photo."""
        self.last_state = Flow.POSITION
        user = update.message.from_user
        self.logger.info("Position of %s: %s", user.first_name, update.message.text)
        position = next((p for p in self.positions if p.name == update.message.text), None)
        if not position:
            await update.message.reply_text("Position not found")
            buttons2 = [[KeyboardButton(position.name)] for position in self.positions]
            reply_markup = ReplyKeyboardMarkup(buttons2, one_time_keyboard=True,
                                               input_field_placeholder=Flow.POSITION.name)
            await update.message.reply_text(
                "What Position are you looking for?",
                reply_markup=reply_markup,
            )
            return Flow.POSITION

        await update.message.reply_text(
            "I see! Please send me a photo of yourself, "
            "so I know what you look like, or send /skip if you don't want to.",
            reply_markup=ReplyKeyboardRemove(),
        )

        return Flow.ADDRESS

    async def address(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Stores the photo and asks for a location."""
        user = update.message.from_user
        photo_file = await update.message.photo[-1].get_file()
        await photo_file.download_to_drive("user_photo.jpg")
        self.logger.info("Photo of %s: %s", user.first_name, "user_photo.jpg")
        await update.message.reply_text(
            "Gorgeous! Now, send me your location please, or send /skip if you don't want to."
        )

        return Flow.FILTERS.value

    async def filter(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Stores the location and asks for some info about the user."""
        user = update.message.from_user
        user_location = update.message.location
        self.logger.info(
            "Location of %s: %f / %f", user.first_name, user_location.latitude, user_location.longitude
        )
        await update.message.reply_text(
            "Maybe I can visit you sometime! At last, tell me something about yourself."
        )

        return Flow.EXPERIENCE.value

    async def skip_filter(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Skips the location and asks for info about the user."""
        user = update.message.from_user
        self.logger.info("User %s did not send a location.", user.first_name)
        await update.message.reply_text(
            "You seem a bit paranoid! At last, tell me something about yourself."
        )

        return Flow.EXPERIENCE.value

    async def experience(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Stores the info about the user and ends the conversation."""
        user = update.message.from_user
        self.logger.info("Bio of %s: %s", user.first_name, update.message.text)
        await update.message.reply_text("Thank you! I hope we can talk again some day.")

        return ConversationHandler.END

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancels and ends the conversation."""
        user = update.message.from_user
        self.logger.info("User %s canceled the conversation.", user.first_name)
        await update.message.reply_text(
            "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
        )

        return ConversationHandler.END

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.logger.info("start handling")
        # chat: Chat = update.message.chat
        # chat.id - 368620919
        # chat.username - 'Qw1zeR'
        # chat.full_name - 'Qw1zeR'
        # user = User(full_name=chat.full_name, username=chat.username, chat_id=chat.id)
        # self.user_repository.insert_user(user)
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
        Flow.POSITION: [MessageHandler(filters.TEXT, start_handler.position)]
        # Flow.SAVE_POSITION: [MessageHandler(filters.TEXT, start_handler.position)]
        # Flow.ADDRESS: [MessageHandler(filters.PHOTO, photo), CommandHandler("skip", skip_photo)],
        # Flow.FILTERS: [
        #     MessageHandler(filters.LOCATION, location),
        #     CommandHandler("skip", skip_location),
        # ],
        # Flow.EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, bio)],
    },
    fallbacks=[CommandHandler("cancel", start_handler.cancel)],
)
