"""
jobspy.scrapers.ziprecruiter
~~~~~~~~~~~~~~~~~~~

This module contains routines to scrape ZipRecruiter.
"""
import math
import time
import re
from datetime import datetime, date
from typing import Optional, Tuple, Any

import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

from .. import Scraper, ScraperInput, Site
from ..exceptions import ZipRecruiterException
from ..utils import count_urgent_words, extract_emails_from_text, create_session
from ...jobs import JobPost, Compensation, Location, JobResponse, JobType, Country


class ZipRecruiterScraper(Scraper):
    def __init__(self, proxy: Optional[str] = None):
        """
        Initializes ZipRecruiterScraper with the ZipRecruiter job search url
        """
        site = Site(Site.ZIP_RECRUITER)
        self.url = "https://www.ziprecruiter.com"
        self.session = create_session(proxy)
        self.get_cookies()
        super().__init__(site, proxy=proxy)

        self.jobs_per_page = 20
        self.seen_urls = set()

    def find_jobs_in_page(
        self, scraper_input: ScraperInput, continue_token: str | None = None
    ) -> Tuple[list[JobPost], Optional[str]]:
        """
        Scrapes a page of ZipRecruiter for jobs with scraper_input criteria
        :param scraper_input:
        :param continue_token:
        :return: jobs found on page
        """
        params = self.add_params(scraper_input)
        if continue_token:
            params["continue"] = continue_token
        try:
            response = self.session.get(
                f"https://api.ziprecruiter.com/jobs-app/jobs",
                headers=self.headers(),
                params=self.add_params(scraper_input),
            )
            if response.status_code != 200:
                raise ZipRecruiterException(
                    f"bad response status code: {response.status_code}"
                )
        except Exception as e:
            if "Proxy responded with non 200 code" in str(e):
                raise ZipRecruiterException("bad proxy")
            raise ZipRecruiterException(str(e))

        time.sleep(5)
        response_data = response.json()
        jobs_list = response_data.get("jobs", [])
        next_continue_token = response_data.get("continue", None)

        with ThreadPoolExecutor(max_workers=self.jobs_per_page) as executor:
            job_results = [executor.submit(self.process_job, job) for job in jobs_list]

        job_list = [result.result() for result in job_results if result.result()]
        return job_list, next_continue_token

    def scrape(self, scraper_input: ScraperInput) -> JobResponse:
        """
        Scrapes ZipRecruiter for jobs with scraper_input criteria.
        :param scraper_input: Information about job search criteria.
        :return: JobResponse containing a list of jobs.
        """
        job_list: list[JobPost] = []
        continue_token = None

        max_pages = math.ceil(scraper_input.results_wanted / self.jobs_per_page)

        for page in range(1, max_pages + 1):
            if len(job_list) >= scraper_input.results_wanted:
                break

            jobs_on_page, continue_token = self.find_jobs_in_page(
                scraper_input, continue_token
            )
            if jobs_on_page:
                job_list.extend(jobs_on_page)

            if not continue_token:
                break

        if len(job_list) > scraper_input.results_wanted:
            job_list = job_list[: scraper_input.results_wanted]

        return JobResponse(jobs=job_list)

    @staticmethod
    def process_job(job: dict) -> JobPost:
        """Processes an individual job dict from the response"""
        title = job.get("name")
        job_url = job.get("job_url")

        description = BeautifulSoup(
            job.get("job_description", "").strip(), "html.parser"
        ).get_text()

        company = job["hiring_company"].get("name") if "hiring_company" in job else None
        country_value = "usa" if job.get("job_country") == "US" else "canada"
        country_enum = Country.from_string(country_value)

        location = Location(
            city=job.get("job_city"), state=job.get("job_state"), country=country_enum
        )
        job_type = ZipRecruiterScraper.get_job_type_enum(
            job.get("employment_type", "").replace("_", "").lower()
        )

        save_job_url = job.get("SaveJobURL", "")
        posted_time_match = re.search(
            r"posted_time=(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)", save_job_url
        )
        if posted_time_match:
            date_time_str = posted_time_match.group(1)
            date_posted_obj = datetime.strptime(date_time_str, "%Y-%m-%dT%H:%M:%SZ")
            date_posted = date_posted_obj.date()
        else:
            date_posted = date.today()

        return JobPost(
            title=title,
            company_name=company,
            location=location,
            job_type=job_type,
            compensation=Compensation(
                interval="yearly"
                if job.get("compensation_interval") == "annual"
                else job.get("compensation_interval"),
                min_amount=int(job["compensation_min"])
                if "compensation_min" in job
                else None,
                max_amount=int(job["compensation_max"])
                if "compensation_max" in job
                else None,
                currency=job.get("compensation_currency"),
            ),
            date_posted=date_posted,
            job_url=job_url,
            description=description,
            emails=extract_emails_from_text(description) if description else None,
            num_urgent_words=count_urgent_words(description) if description else None,
        )

    def get_cookies(self):
        url="https://api.ziprecruiter.com/jobs-app/event"
        data="event_type=session&logged_in=false&number_of_retry=1&property=model%3AiPhone&property=os%3AiOS&property=locale%3Aen_us&property=app_build_number%3A4734&property=app_version%3A91.0&property=manufacturer%3AApple&property=timestamp%3A2024-01-12T12%3A04%3A42-06%3A00&property=screen_height%3A852&property=os_version%3A16.6.1&property=source%3Ainstall&property=screen_width%3A393&property=device_model%3AiPhone%2014%20Pro&property=brand%3AApple"
        self.session.post(url, data=data, headers=ZipRecruiterScraper.headers())

    @staticmethod
    def get_job_type_enum(job_type_str: str) -> list[JobType] | None:
        for job_type in JobType:
            if job_type_str in job_type.value:
                return [job_type]
        return None

    @staticmethod
    def add_params(scraper_input) -> dict[str, str | Any]:
        params = {
            "search": scraper_input.search_term,
            "location": scraper_input.location,
            "form": "jobs-landing",
        }
        job_type_value = None
        if scraper_input.job_type:
            if scraper_input.job_type.value == "fulltime":
                job_type_value = "full_time"
            elif scraper_input.job_type.value == "parttime":
                job_type_value = "part_time"
            else:
                job_type_value = scraper_input.job_type.value

        if job_type_value:
            params[
                "refine_by_employment"
            ] = f"employment_type:employment_type:{job_type_value}"

        if scraper_input.is_remote:
            params["refine_by_location_type"] = "only_remote"

        if scraper_input.distance:
            params["radius"] = scraper_input.distance

        return params

    @staticmethod
    def headers() -> dict:
        """
        Returns headers needed for requests
        :return: dict - Dictionary containing headers
        """
        return {
            "Host": "api.ziprecruiter.com",
            "accept": "*/*",
            "x-zr-zva-override": "100000000;vid:ZT1huzm_EQlDTVEc",
            "x-pushnotificationid": "0ff4983d38d7fc5b3370297f2bcffcf4b3321c418f5c22dd152a0264707602a0",
            "x-deviceid": "D77B3A92-E589-46A4-8A39-6EF6F1D86006",
            "user-agent": "Job Search/87.0 (iPhone; CPU iOS 16_6_1 like Mac OS X)",
            "authorization": "Basic YTBlZjMyZDYtN2I0Yy00MWVkLWEyODMtYTI1NDAzMzI0YTcyOg==",
            "accept-language": "en-US,en;q=0.9",
        }
