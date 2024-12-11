import os
from typing import List
from pymongo import MongoClient, UpdateOne

from jobspy.jobs import JobPost


class JobRepository:

    def __init__(self):
        self.mongoUri = os.getenv("MONGO_URI")
        # Connect to MongoDB server
        self.client = MongoClient(self.mongoUri)
        # Access a database (it will be created automatically if it doesn't exist)
        self.db = self.client["jobs_database"]
        # Access a collection
        self.collection = self.db["jobs"]

    def insert_or_update_job(self, job: JobPost):
        # Convert JobPost to dictionary
        job_dict = job.model_dump(exclude={"date_posted"})

        # Check if the job already exists by its ID
        if job.id:
            # If it exists, update the `updated_at` field and other fields
            # job_dict['updated_at'] = datetime.utcnow()  # Set updated time to current time
            self.collection.update_one(
                {'_id': job.id},
                {'$set': job_dict}
            )
            print(f"Updated job with ID {job.id}.")
        else:
            # If it doesn't exist, insert a new job with the current `created_at` and `updated_at`
            self.collection.insert_one(job_dict)
            print(f"Inserted new job with title {job.title}.")

    def insertManyIfNotFound(self, jobs: List[JobPost]) -> List[JobPost]:
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
                    # Only set fields if the job is being inserted (not updated)
                    {"$setOnInsert": job_dict},
                    upsert=True  # Insert if not found, but do not update if already exists
                )
            )

        if operations:
            # Execute all operations in bulk
            result = self.collection.bulk_write(operations)
            print(f"Matched: {result.matched_count}, Upserts: {
                  result.upserted_count}, Modified: {result.modified_count}")

            # Get the newly inserted jobs (those that were upserted)
            # The `upserted_count` corresponds to how many new documents were inserted
            for i, job in enumerate(jobs):
                if result.upserted_count > 0 and i < result.upserted_count:
                    new_jobs.append(job)
                    print(f"New Job ID: {job.id}, Label: {job.title}")

        return new_jobs
