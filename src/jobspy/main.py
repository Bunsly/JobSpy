import asyncio
import re
from jobspy import Site, scrape_jobs
from jobspy.db.job_repository import JobRepository
from jobspy.jobs import JobPost
from jobspy.telegram_bot import TelegramBot

filter_by_title: list[str] = ["test", "qa", "Lead", "Full Stack", "Fullstack", "Frontend"
                              "data", "automation", "BI", "Principal"]


def filter_jobs_by_title_name(job: JobPost):
    for filter_title in filter_by_title:
        if re.search(filter_title, job.title, re.IGNORECASE):
            return False

    return True


async def main():
    telegramBot = TelegramBot()
    jobRepository = JobRepository()

    jobs = scrape_jobs(
        site_name=[Site.LINKEDIN, Site.GLASSDOOR, Site.INDEED],
        # site_name=[Site.GOOZALI],
        search_term="software engineer",
        google_search_term="software engineer jobs near Tel Aviv Israel since yesterday",
        locations=["Tel Aviv, Israel", "Ramat Gan, Israel",
                   "Central, Israel", "Rehovot ,Israel"],
        results_wanted=200,
        hours_old=200,
        country_indeed='israel',
    )
    print(f"Found {len(jobs)} jobs")
    job = filter(filter_jobs_by_title_name, jobs)

    newJobs = jobRepository.insertManyIfNotFound(jobs)

    for newJob in newJobs:
        await telegramBot.sendJob(newJob)

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())
