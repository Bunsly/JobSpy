import os

from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

from src.jobspy import Site
from src.jobspy.scrapers.utils import create_logger
from src.telegram_handler import TelegramIndeedHandler, TelegramDefaultHandler
from src.telegram_handler.telegram_callback_handler import TelegramCallHandler

logger = create_logger("Main")
title_filters: list[str] = ["test", "qa", "Lead", "Full-Stack", "Full Stack", "Fullstack", "Frontend", "Front-end",
                            "Front End", "DevOps", "Physical", "Staff",
                            "automation", "BI ", "Principal", "Architect", "Android", "Machine Learning", "Student",
                            "Data Engineer", "DevSecOps"]

if __name__ == "__main__":
    logger.info("Starting initialize ")
    _api_token = os.getenv("TELEGRAM_API_TOKEN")
    search_term = "software engineer"
    locations = ["Tel Aviv, Israel", "Ramat Gan, Israel", "Central, Israel", "Rehovot ,Israel"]
    application = Application.builder().token(_api_token).build()
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
    application.add_handler(CommandHandler(Site.GOOZALI.value, tg_handler_goozali.handle))
    # GlassDoor
    tg_handler_glassdoor = TelegramDefaultHandler(sites=[Site.GLASSDOOR],
                                                  locations=locations,
                                                  title_filters=title_filters,
                                                  search_term=search_term)
    application.add_handler(CommandHandler(Site.GLASSDOOR.value, tg_handler_glassdoor.handle))
    # LinkeDin
    tg_handler_linkedin = TelegramDefaultHandler(sites=[Site.LINKEDIN],
                                                 locations=locations,
                                                 title_filters=title_filters,
                                                 search_term=search_term)
    application.add_handler(CommandHandler(Site.LINKEDIN.value, tg_handler_linkedin.handle))
    # Indeed
    tg_handler_indeed = TelegramIndeedHandler(locations=locations,
                                              title_filters=title_filters,
                                              search_term=search_term)
    application.add_handler(CommandHandler(Site.INDEED.value, tg_handler_indeed.handle))
    application.add_handler(CallbackQueryHandler(tg_callback_handler.button_callback))
    logger.info("Run polling from telegram")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
