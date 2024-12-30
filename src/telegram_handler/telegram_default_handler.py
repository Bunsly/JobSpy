from telegram import Update
from telegram.constants import ReactionEmoji
from telegram.ext import (
    ContextTypes,
)

from db.job_repository import JobRepository
from jobspy import Site, scrape_jobs
from jobspy.scrapers.utils import create_logger
from telegram_bot import TelegramBot
from telegram_handler.telegram_handler import TelegramHandler


class TelegramDefaultHandler(TelegramHandler):
    def __init__(self, sites: list[Site], locations: list[str], title_filters: list[str], search_term: str):
        self.sites_to_scrap = sites
        self.locations = locations
        self.search_term = search_term
        self.title_filters = title_filters
        self.telegram_bot = TelegramBot()
        self.jobRepository = JobRepository()
        if len(sites) == 1:
            self.logger = create_logger(
                f"Telegram{sites[0].name.title()}Handler")
        else:
            self.logger = create_logger("TelegramAllHandler")

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.logger.info("start handling")
        await self.telegram_bot.set_message_reaction(
            update.message.message_id, ReactionEmoji.FIRE)
        site_names = [site.name for site in self.sites_to_scrap]
        await self.telegram_bot.send_text(
            f"Start scarping: {", ".join(site_names)}")
        jobs = scrape_jobs(
            site_name=self.sites_to_scrap,
            search_term=self.search_term,
            locations=self.locations,
            results_wanted=200,
            hours_old=48,
            filter_by_title=self.title_filters
        )
        self.logger.info(f"Found {len(jobs)} jobs")
        new_jobs = self.jobRepository.insertManyIfNotFound(jobs)
        for newJob in new_jobs:
            await self.telegram_bot.send_job(newJob)
        await self.telegram_bot.send_text(
                f"Finished scarping: {self.sites_to_scrap[0].name}")
        self.logger.info("finished handling")
