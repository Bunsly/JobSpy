from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ReactionEmoji
from telegram.ext import (
    ContextTypes,
)

from model.job_repository import JobRepository
from jobspy import Site, scrape_jobs, JobPost
from jobspy.scrapers.utils import create_logger
from telegram_bot import TelegramBot
from telegram_handler.telegram_handler import TelegramHandler


def map_jobs_to_keyboard(jobs: list[JobPost]) -> InlineKeyboardMarkup:
    """
    Maps a list of JobPost objects to a list of lists of InlineKeyboardButton objects.

    Args:
        jobs: A list of JobPost objects.

    Returns:
        A list of lists of InlineKeyboardButton objects, where each inner list contains
        a single button representing a job.
    """
    keyboard = []
    for job in jobs:
        # Create a new inner list for each job
        inner_list = [InlineKeyboardButton(f"{job.title},{job.company_name}", callback_data=job.id)]
        # Append the inner list to the main keyboard list
        keyboard.append(inner_list)

    return InlineKeyboardMarkup(keyboard)


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
        chat_id = update.message.chat.id
        await self.telegram_bot.set_message_reaction(chat_id,
                                                     update.message.message_id, ReactionEmoji.FIRE)
        site_names = [site.name for site in self.sites_to_scrap]
        site_names_print = ", ".join(site_names)
        await self.telegram_bot.send_text(chat_id,
                                          f"Start scarping: {site_names_print}")
        filtered_out_jobs, jobs = scrape_jobs(
            site_name=self.sites_to_scrap,
            search_term=self.search_term,
            locations=self.locations,
            results_wanted=200,
            hours_old=48,
            filter_by_title=self.title_filters,
            country_indeed='israel'
        )
        self.logger.info(f"Found {len(jobs)} jobs")
        self.jobRepository.insert_many_if_not_found(filtered_out_jobs)
        old_jobs, new_jobs = self.jobRepository.insert_many_if_not_found(jobs)
        for newJob in new_jobs:
            await self.telegram_bot.send_job(chat_id, newJob)
        if filtered_out_jobs:
            await self.telegram_bot.send_text(chat_id, "filtered by title: ",
                                              reply_markup=map_jobs_to_keyboard(filtered_out_jobs))
        self.logger.info(f"Found {len(old_jobs)} old jobs")
        await self.telegram_bot.send_text(chat_id,
                                          f"Finished scarping: {site_names_print}")
        self.logger.info("finished handling")
