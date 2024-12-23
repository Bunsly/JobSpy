import asyncio
import re
from jobspy import Site, scrape_jobs
from jobspy.db.job_repository import JobRepository
from jobspy.jobs import JobPost
from jobspy.scrapers.utils import create_logger
from jobspy.telegram_bot import TelegramBot

logger = create_logger("Main")
filter_by_title: list[str] = ["test", "qa", "Lead", "Full-Stack", "Full Stack", "Fullstack", "Frontend", "Front-end", "Front End", "DevOps", "Physical", "Staff",
                              "automation", "BI", "Principal", "Architect", "Android", "Machine Learning", "Student", "Data Engineer", "DevSecOps"]


def filter_jobs_by_title_name(job: JobPost):
    for filter_title in filter_by_title:
        if re.search(filter_title, job.title, re.IGNORECASE):
            logger.info(f"job filtered out by title: {job.id} , {
                        job.title} , found {filter_title}")
            return False

    return True


async def main():
    telegramBot = TelegramBot()
    jobRepository = JobRepository()
    # sites_to_scrap = [Site.LINKEDIN, Site.GLASSDOOR, Site.INDEED, Site.GOOZALI]
    sites_to_scrap = [Site.GLASSDOOR]
    # sites_to_scrap = [Site.GOOZALI]
    jobs = scrape_jobs(
        site_name=sites_to_scrap,
        search_term="software engineer",
        google_search_term="software engineer jobs near Tel Aviv Israel since yesterday",
        locations=["Tel Aviv, Israel", "Ramat Gan, Israel",
                   "Central, Israel", "Rehovot ,Israel"],
        results_wanted=200,
        hours_old=48,
        country_indeed='israel'
    )
    logger.info(f"Found {len(jobs)} jobs")
    jobs = list(filter(filter_jobs_by_title_name, jobs))
    newJobs = jobRepository.insertManyIfNotFound(jobs)
    for newJob in newJobs:
        await telegramBot.sendJob(newJob)

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())
