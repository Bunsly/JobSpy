import os

from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, Updater

from jobspy.scrapers.site import Site
from jobspy.scrapers.utils import create_logger
from telegram_handler import TelegramDefaultHandler
from telegram_handler.button_callback.telegram_callback_handler import TelegramCallHandler

logger = create_logger("Main")
_api_token = os.getenv("TELEGRAM_API_TOKEN")
application = Application.builder().token(_api_token).build()
title_filters: list[str] = ["test", "qa", "Lead", "Full-Stack", "Full Stack", "Fullstack", "Frontend", "Front-end",
                            "Front End", "DevOps", "Physical", "Staff",
                            "automation", "BI ", "Principal", "Architect", "Android", "Machine Learning", "Student",
                            "Data Engineer", "DevSecOps"]


async def stop(update, context):
    logger.info("Stop polling from telegram")
    application.stop_running()

if __name__ == "__main__":
    logger.info("Starting initialize ")
    search_term = "software engineer"
    locations = ["Tel Aviv, Israel", "Ramat Gan, Israel",
                 "Central, Israel", "Rehovot ,Israel"]
    tg_callback_handler = TelegramCallHandler()
    tg_handler_all = TelegramDefaultHandler(sites=[Site.LINKEDIN, Site.GLASSDOOR, Site.INDEED, Site.GOOZALI],
                                            locations=locations,
                                            title_filters=title_filters,
                                            search_term=search_term)
    application.add_handler(CommandHandler("find", tg_handler_all.handle))
    # Goozali
    tg_handler_goozali = TelegramDefaultHandler(sites=[Site.GOOZALI],
                                                locations=locations,
                                                title_filters=title_filters,
                                                search_term=search_term)
    application.add_handler(CommandHandler(
        Site.GOOZALI.value, tg_handler_goozali.handle))
    # GlassDoor
    tg_handler_glassdoor = TelegramDefaultHandler(sites=[Site.GLASSDOOR],
                                                  locations=locations,
                                                  title_filters=title_filters,
                                                  search_term=search_term)
    application.add_handler(CommandHandler(
        Site.GLASSDOOR.value, tg_handler_glassdoor.handle))
    # LinkeDin
    tg_handler_linkedin = TelegramDefaultHandler(sites=[Site.LINKEDIN],
                                                 locations=locations,
                                                 title_filters=title_filters,
                                                 search_term=search_term)
    application.add_handler(CommandHandler(
        Site.LINKEDIN.value, tg_handler_linkedin.handle))
    # Indeed
    tg_handler_indeed = TelegramDefaultHandler(sites=[Site.INDEED],
                                               locations=locations,
                                               title_filters=title_filters,
                                               search_term=search_term)
    application.add_handler(CommandHandler(
        Site.INDEED.value, tg_handler_indeed.handle))
    application.add_handler(CallbackQueryHandler(
        tg_callback_handler.button_callback))
    application.add_handler(CommandHandler('stop', stop))
    logger.info("Run polling from telegram")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
