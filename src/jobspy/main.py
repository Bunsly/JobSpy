import asyncio
from jobspy import Site, scrape_jobs
from jobspy.db.job_repository import JobRepository
from jobspy.telegram_bot import TelegramBot


async def main():
    telegramBot = TelegramBot()
    jobRepository = JobRepository()

    jobs = scrape_jobs(
        # site_name=[Site.LINKEDIN, Site.GOOZALI, Site.GLASSDOOR, Site.INDEED],
        site_name=[Site.GOOZALI],
        search_term="software engineer",
        google_search_term="software engineer jobs near Tel Aviv Israel since yesterday",
        location="Central, Israel",
        # locations=["Rehovot"],
        locations=["Tel Aviv, Israel", "Ramat Gan, Israel",
                   "Central, Israel", "Rehovot ,Israel"],
        results_wanted=200,
        hours_old=200,
        country_indeed='israel',
    )
    print(f"Found {len(jobs)} jobs")

    newJobs = jobRepository.insertManyIfNotFound(jobs)

    for newJob in newJobs:
        await telegramBot.sendJob(newJob)

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())
