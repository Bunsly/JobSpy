from dotenv import load_dotenv

from model.job_repository import JobRepository
from tests.test_util import createMockJob

load_dotenv()


class DatabaseTests:

    def __init__(self):
        """
        This block ensures that the script runs the test only when executed directly,
        not when imported as a module.
        """
        self.jobRepository = JobRepository()

    def insert_job(self):
        """
        Inserts a mock job into the database using JobRepository.
        """
        job = createMockJob()
        self.jobRepository.insert_job(job)
        print(f"Job inserted successfully.{job.id}")


if __name__ == '__main__':
    # Create an instance of DatabaseTests
    tests = DatabaseTests()

    # Run the insert_job test
    tests.insert_job()
