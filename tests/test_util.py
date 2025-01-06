from datetime import datetime, date
from typing import List

from scrapers import JobPost, Location, Country


# Creating some test job posts


def createMockJob() -> JobPost:
    return JobPost(
        id='li-4072458658',
        title='Backend Developer',
        company_name='Okoora',
        job_url='https://www.linkedin.com/jobs/view/4072458658',
        location=Location(country=Country.ISRAEL,
                          city='Ramat Gan', state='Tel Aviv District'),
        description=None,
        company_url='https://ch.linkedin.com/company/okoora',
        date_posted=date(2024, 12, 9),
        datetime_posted=datetime(2024, 12, 9)
    )


def createMockJob2() -> JobPost:
    return JobPost(
        id='li-4093541744',
        title='Software Engineer',
        company_name='Hyro',
        job_url='https://www.linkedin.com/jobs/view/4093541744',
        location=Location(country=Country.ISRAEL,
                          city='Tel Aviv-Yafo', state='Tel Aviv District'),
        description=None,
        company_url='https://www.linkedin.com/company/hyroai',
        date_posted=date(2024, 12, 8),
        datetime_posted=datetime(2024, 12, 8)
    )


def createMockJob3() -> JobPost:
    return JobPost(
        id='li-4090995419',
        title='Frontend Developer',
        company_name='Balance',
        job_url='https://www.linkedin.com/jobs/view/4090995419',
        location=Location(country=Country.WORLDWIDE,
                          city='Tel Aviv District', state='Israel'),
        description=None,
        company_url='https://www.linkedin.com/company/getbalance',
        date_posted=date(2024, 12, 5),
        datetime_posted=datetime(2024, 12, 5)
    )


def createMockJob4() -> JobPost:
    return JobPost(
        id='li-4090533760',
        title='Backend Developer',
        company_name='Vi',
        job_url='https://www.linkedin.com/jobs/view/4090533760',
        location=Location(country=Country.ISRAEL,
                          city='Tel Aviv-Yafo', state='Tel Aviv District'),
        description=None,
        company_url='https://www.linkedin.com/company/vi',
        date_posted=date(2024, 12, 3),
        datetime_posted=datetime(2024, 12, 3)
    )


def createMockJob5() -> JobPost:
    return JobPost(
        id='li-4074568220',
        title='Backend .NET Developer',
        company_name='Just Eat Takeaway.com',
        job_url='https://www.linkedin.com/jobs/view/4074568220',
        location=Location(country=Country.WORLDWIDE,
                          city='Tel Aviv District', state='Israel'),
        description=None,
        company_url='https://nl.linkedin.com/company/just-eat-takeaway-com',
        date_posted=date(2024, 12, 6),
        datetime_posted=datetime(2024, 12, 6)
    )


def createMockjobs() -> List[JobPost]:

    return [createMockJob(), createMockJob2(), createMockJob3(),
            createMockJob4(), createMockJob5()]
