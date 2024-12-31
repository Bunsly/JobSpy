from dotenv import load_dotenv
from pymongo import UpdateOne

from .monogo_db import MongoDB
from jobspy import create_logger
from jobspy.jobs import JobPost

load_dotenv()


class JobRepository:
    _instance = None

    def __new__(cls):

        if cls._instance is not None:
            return cls._instance

        self = super().__new__(cls)
        cls._instance = self
        self.logger = create_logger("JobRepository")
        mongo_client = MongoDB()
        self.collection = mongo_client.db["jobs"]
        self.logger.info("Succeed connect to MongoDB")
        return cls._instance

    def insert_job(self, job: JobPost):
        job_dict = job.model_dump(exclude={"date_posted"})
        self.collection.insert_one(job_dict)
        self.logger.info(f"Inserted new job with title {job.title}.")

    def insert_many_if_not_found(self, jobs: list[JobPost]) -> tuple[list[JobPost],list[JobPost]]:
        """
        Perform bulk upserts for a list of JobPost objects into a MongoDB collection.
        Only insert new jobs and return the list of newly inserted jobs.
        """
        operations = []
        new_jobs = []  # List to store the new jobs inserted into MongoDB
        old_jobs = []  # List to store the new jobs inserted into MongoDB
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
                else:
                    old_jobs.append(job)

        return old_jobs ,new_jobs
