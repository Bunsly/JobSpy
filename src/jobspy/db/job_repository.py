import os
from typing import List
from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne
import pymongo

from jobspy.jobs import JobPost

load_dotenv()


class JobRepository:

    def __init__(self, database_name: str = None):
        self.mongoUri = os.getenv("MONGO_URI")
        if not self.mongoUri:
            raise ValueError("MONGO_URI environment variable is not set")
        self.client = MongoClient(self.mongoUri)
        if database_name is None:
            database_name = os.getenv("MONGO_DB_NAME")
            if not database_name:
                raise ValueError(
                    "MONGO_DB_NAME environment variable is not set")
        self.db = self.client[database_name]
        self.collection = self.db["jobs"]

    def insert_job(self, job: JobPost):
        job_dict = job.model_dump(exclude={"date_posted"})
        self.collection.insert_one(job_dict)
        print(f"Inserted new job with title {job.title}.")

    # def insertManyIfNotFound(self, jobs: List[JobPost]) -> List[JobPost]:
    #     """
    #     Perform bulk upserts for a list of JobPost objects into a MongoDB collection.
    #     Only insert new jobs and return the list of newly inserted jobs.
    #     """
    #     operations = []
    #     new_jobs = []  # List to store the new jobs inserted into MongoDB
    #     for job in jobs:
    #         job_dict = job.model_dump(exclude={"date_posted"})
    #         operations.append(
    #             UpdateOne(
    #                 {"id": job.id},  # Match by `id`
    #                 # Only set fields if the job is being inserted (not updated)
    #                 {"$setOnInsert": job_dict},
    #                 upsert=True  # Insert if not found, but do not update if already exists
    #             )
    #         )

    #     if operations:
    #         # Execute all operations in bulk
    #         result = self.collection.bulk_write(operations)
    #         print(f"Matched: {result.matched_count}, Upserts: {
    #               result.upserted_count}, Modified: {result.modified_count}")

    #         # Get the newly inserted jobs (those that were upserted)
    #         # The `upserted_count` corresponds to how many new documents were inserted
    #         for i, job in enumerate(jobs):
    #             if result.upserted_count > 0 and i < result.upserted_count:
    #                 new_jobs.append(job)
    #                 print(f"New Job ID: {job.id}, Label: {job.title}")

    #     return new_jobs

    def insertManyIfNotFound(self, jobs: List[JobPost]) -> List[JobPost]:
        """
        Perform bulk inserts for a list of JobPost objects into a MongoDB collection.
        Only insert new jobs and return the list of newly inserted jobs.
        Args:
            jobs (List[JobPost]): List of JobPost objects to insert.
        Returns:
            List[JobPost]: List of newly inserted JobPost objects.

        Raises:
            pymongo.errors.BulkWriteError: If an error occurs during the bulk insert.
        """
        new_jobs = []
        result = self.collection.insert_many(jobs)
        new_jobs = [jobs[i] for i, _ in enumerate(
            result.inserted_ids) if result.inserted_ids]
        print(f"Inserted Jobs: {len(new_jobs)}")

        return new_jobs
