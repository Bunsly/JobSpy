from jobspy.db.job_repository import JobRepository
from tests.test_util import createMockJob


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
        self.jobRepository.insert_or_update_job(job)
        print("Job inserted successfully.")


if __name__ == '__main__':
    # Create an instance of DatabaseTests
    tests = DatabaseTests()

    # Run the insert_job test
    tests.insert_job()
