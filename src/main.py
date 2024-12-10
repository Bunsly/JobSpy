import asyncio
import csv
from typing import List

from pymongo import MongoClient, UpdateOne
from telegram import Bot

from jobspy import scrape_jobs
from jobspy.jobs import JobPost 
TELEGRAM_API_TOKEN = 
CHAT_ID = 
# Connect to MongoDB server
client = MongoClient("mongodb://localhost:27017/")
# Access a database (it will be created automatically if it doesn't exist)
db = client["jobs_database"]
# Access a collection
jobs_collection = db["jobs"]
# Initialize the Telegram bot
bot = Bot(token=TELEGRAM_API_TOKEN)

async def send_job_to_telegram(job:JobPost):
    """
    Send job details to Telegram chat.
    """
    message = f"New Job Posted:\n\n" \
              f"Job ID: {job.id}\n" \
              f"Job Title: {job.title}\n" \
              f"Company: {job.company_name}\n" \
              f"Location: {job.location}\n" \
              f"Link: {job.job_url}\n"
    try:
        await bot.sendMessage(chat_id=CHAT_ID, text=message)
        print(f"Sent job to Telegram: {job.id}")
    except Exception as e:
        print(f"Failed to send job to Telegram: {e}")

def insert_jobs(jobs: List[JobPost], collection):
    """
    Perform bulk upserts for a list of JobPost objects into a MongoDB collection.
    Only insert new jobs and return the list of newly inserted jobs.
    """
    operations = []
    new_jobs = []  # List to store the new jobs inserted into MongoDB

    for job in jobs:
        job_dict = job.model_dump(exclude={"date_posted"})
        operations.append(
            UpdateOne(
                {"id": job.id},  # Match by `id`
                {"$setOnInsert": job_dict},  # Only set fields if the job is being inserted (not updated)
                upsert=True  # Insert if not found, but do not update if already exists
            )
        )

    if operations:
        # Execute all operations in bulk
        result = collection.bulk_write(operations)
        print(f"Matched: {result.matched_count}, Upserts: {result.upserted_count}, Modified: {result.modified_count}")

        # Get the newly inserted jobs (those that were upserted)
        # The `upserted_count` corresponds to how many new documents were inserted
        for i, job in enumerate(jobs):
            if result.upserted_count > 0 and i < result.upserted_count:
                new_jobs.append(job)
                print(f"New Job ID: {job.id}, Label: {job.title}")

    return new_jobs

async def main():

    jobs = scrape_jobs(
        # site_name=["indeed", "linkedin", "zip_recruiter", "glassdoor", "google"],
        site_name=["glassdoor"],
        search_term="software engineer",
        google_search_term="software engineer jobs near Tel Aviv Israel since yesterday",
        location="Central, Israel",
        locations=["Ramat Gan, Israel"],
        # locations=["Tel Aviv, Israel","Ramat Gan, Israel","Central, Israel","Rehovot ,Israel"],
        results_wanted=50,
        hours_old=200,
        country_indeed='israel',
    )
    print(f"Found {len(jobs)} jobs")

    new_jobs = insert_jobs(jobs, jobs_collection)

    for new_job in new_jobs:
        await send_job_to_telegram(new_job)
    # Run the async main function
if __name__ == "__main__":
    asyncio.run(main())