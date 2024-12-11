from jobspy.db.job_repository import JobRepository
from tests.test_util import createMockJob


def insert_job():
    jobRepository = JobRepository()
    job = createMockJob()
    jobRepository.insert_or_update_job(job)
