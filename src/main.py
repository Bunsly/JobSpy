from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, ConversationHandler, \
    MessageHandler, filters, ContextTypes

from config.settings import settings
from jobspy.scrapers.utils import create_logger
from telegram_handler.telegram_start_handler import start_conv_handler

logger = create_logger("Main")
_api_token = settings.telegram_api_token
application = Application.builder().token(_api_token).build()
title_filters: list[str] = ["test", "qa", "Lead", "Full-Stack", "Full Stack", "Fullstack", "Frontend", "Front-end",
                            "Front End", "DevOps", "Physical", "Staff",
                            "automation", "BI ", "Principal", "Architect", "Android", "Machine Learning", "Student",
                            "Data Engineer", "DevSecOps"]

if __name__ == "__main__":
    logger.info("Starting initialize ")
    search_term = "software engineer"
    locations = ["Tel Aviv, Israel", "Ramat Gan, Israel",
                 "Central, Israel", "Rehovot ,Israel"]
    application.add_handler(start_conv_handler)

    # application.add_handler(CommandHandler('start', start_handler.handle))
    logger.info("Run polling from telegram")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
