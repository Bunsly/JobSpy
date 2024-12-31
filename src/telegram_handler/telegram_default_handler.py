from telegram import Update
from telegram.constants import ReactionEmoji
from telegram.ext import (
    ContextTypes,
)

from db.job_repository import JobRepository
from jobspy import Site, scrape_jobs, JobPost
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

    async def send_old_job(self, old_jobs: list[JobPost]):

        pass

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.logger.info("start handling")
        await self.telegram_bot.set_message_reaction(
            update.message.message_id, ReactionEmoji.FIRE)
        site_names = [site.name for site in self.sites_to_scrap]
        site_names_print = ", ".join(site_names)
        await self.telegram_bot.send_text(
            f"Start scarping: {site_names_print}")
        filtered_out_jobs, jobs = scrape_jobs(
            site_name=self.sites_to_scrap,
            search_term=self.search_term,
            locations=self.locations,
            results_wanted=200,
            hours_old=48,
            filter_by_title=self.title_filters
        )
        self.logger.info(f"Found {len(jobs)} jobs")
        self.jobRepository.insert_many_if_not_found(filtered_out_jobs)
        old_jobs, new_jobs = self.jobRepository.insert_many_if_not_found(jobs)
        for newJob in new_jobs:
            await self.telegram_bot.send_job(newJob)
        filtered_by_title = [job.title for job in filtered_out_jobs]
        result_string = "filtered by title:\n" + "\n".join(filtered_by_title)
        await self.telegram_bot.send_text(result_string)
        self.logger.info(f"Found {len(old_jobs)} old jobs")
        await self.telegram_bot.send_text(
            f"Finished scarping: {site_names_print}")
        self.logger.info("finished handling")
