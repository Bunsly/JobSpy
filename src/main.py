import os

from telegram import Update
from telegram.ext import Application, CommandHandler

from src.jobspy import Site, scrape_jobs
from src.jobspy.db.job_repository import JobRepository
from src.jobspy.scrapers.utils import create_logger
from src.telegram_bot import TelegramBot
from src.telegram_handler import TelegramAllHandler,TelegramGoozaliHandler

logger = create_logger("Main")
title_filters: list[str] = ["test", "qa", "Lead", "Full-Stack", "Full Stack", "Fullstack", "Frontend", "Front-end",
                            "Front End", "DevOps", "Physical", "Staff",
                            "automation", "BI", "Principal", "Architect", "Android", "Machine Learning", "Student",
                            "Data Engineer", "DevSecOps"]


async def main():
    telegramBot = TelegramBot()
    jobRepository = JobRepository()
    # sites_to_scrap = [Site.LINKEDIN, Site.GLASSDOOR, Site.INDEED, Site.GOOZALI]
    sites_to_scrap = [Site.GOOZALI]
    # sites_to_scrap = [Site.GOOZALI]
    jobs = scrape_jobs(
        site_name=sites_to_scrap,
        search_term="software engineer",
        locations=["Tel Aviv, Israel", "Ramat Gan, Israel",
                   "Central, Israel", "Rehovot ,Israel"],
        results_wanted=200,
        hours_old=48,
        country_indeed='israel'
    )
    logger.info(f"Found {len(jobs)} jobs")
    newJobs = jobRepository.insertManyIfNotFound(jobs)
    for newJob in newJobs:
        await telegramBot.sendJob(newJob)


# Run the async main function
if __name__ == "__main__":
    logger.info("Starting initialize ")
    _api_token = os.getenv("TELEGRAM_API_TOKEN")
    search_term = "software engineer"
    locations = ["Tel Aviv, Israel", "Ramat Gan, Israel", "Central, Israel", "Rehovot ,Israel"]
    application = Application.builder().token(_api_token).build()
    tg_handler_all = TelegramAllHandler(sites=[Site.LINKEDIN, Site.GLASSDOOR, Site.INDEED, Site.GOOZALI],
                                        locations=locations,
                                        title_filters=title_filters,
                                        search_term=search_term)
    application.add_handler(CommandHandler("findAll", tg_handler_all.handle))
    tg_handler_goozali = TelegramGoozaliHandler(locations=locations,
                                        title_filters=title_filters,
                                        search_term=search_term)
    application.add_handler(CommandHandler("goozali", tg_handler_goozali.handle))
    # application.add_handler(CommandHandler("galssdoor", find_glassdoor))
    # application.add_handler(CommandHandler("linkedin", find_linkedin))
    # application.add_handler(CommandHandler("indeed", find_indeed))
    logger.info("Run polling from telegram")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
