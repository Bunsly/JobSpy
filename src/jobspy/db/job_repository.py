import os
from typing import List
from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne
import pymongo

from .. import create_logger
from ..jobs import JobPost

load_dotenv()


class JobRepository:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(JobRepository, cls).__new__(cls)
        return cls.instance

    def __init__(self, database_name: str = None):
        self.logger = create_logger("JobRepository")
        self.mongoUri = os.getenv("MONGO_URI")
        if not self.mongoUri:
            self.logger.error("MONGO_URI environment variable is not set")
            raise ValueError("MONGO_URI environment variable is not set")
        self.client = MongoClient(self.mongoUri)
        if database_name is None:
            database_name = os.getenv("MONGO_DB_NAME")
            if not database_name:
                self.logger.error("MONGO_DB_NAME environment variable is not set")
                raise ValueError(
                    "MONGO_DB_NAME environment variable is not set")
        self.db = self.client[database_name]
        self.collection = self.db["jobs"]
        self.logger.info("Succeed connect to MongoDB")

    def insert_job(self, job: JobPost):
        job_dict = job.model_dump(exclude={"date_posted"})
        self.collection.insert_one(job_dict)
        self.logger.info(f"Inserted new job with title {job.title}.")

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
            self.logger.info(f"Matched: {result.matched_count}, Upserts: {
                  result.upserted_count}, Modified: {result.modified_count}")

            # Get the newly inserted jobs (those that were upserted)
            # The `upserted_count` corresponds to how many new documents were inserted
            for i, job in enumerate(jobs):
                if result.upserted_count > 0 and i < result.upserted_count:
                    new_jobs.append(job)
                    self.logger.info(f"New Job ID: {job.id}, Label: {job.title}")

        return new_jobs
