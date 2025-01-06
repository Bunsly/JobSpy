from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

from config.settings import settings
from scrapers import Site
from scrapers.utils import create_logger
from telegram_handler import TelegramDefaultHandler
from telegram_handler.button_callback.telegram_callback_handler import TelegramCallHandler
from telegram_handler.telegram_myinfo_handler import my_info_handler
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
    tg_callback_handler = TelegramCallHandler()
    tg_handler_all = TelegramDefaultHandler(sites=[Site.LINKEDIN, Site.GLASSDOOR, Site.INDEED, Site.GOOZALI])
    application.add_handler(CommandHandler("find", tg_handler_all.handle))
    # Goozali
    tg_handler_goozali = TelegramDefaultHandler(sites=[Site.GOOZALI])
    application.add_handler(CommandHandler(
        Site.GOOZALI.value, tg_handler_goozali.handle))
    # GlassDoor
    tg_handler_glassdoor = TelegramDefaultHandler(sites=[Site.GLASSDOOR])
    application.add_handler(CommandHandler(
        Site.GLASSDOOR.value, tg_handler_glassdoor.handle))
    # LinkeDin
    tg_handler_linkedin = TelegramDefaultHandler(sites=[Site.LINKEDIN])
    application.add_handler(CommandHandler(
        Site.LINKEDIN.value, tg_handler_linkedin.handle))
    # Indeed
    tg_handler_indeed = TelegramDefaultHandler(sites=[Site.INDEED])
    application.add_handler(CommandHandler(
        Site.INDEED.value, tg_handler_indeed.handle))
    application.add_handler(CommandHandler(
        "myInfo", my_info_handler.handle))
    application.add_handler(CallbackQueryHandler(
        tg_callback_handler.button_callback))
    logger.info("Run polling from telegram")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
