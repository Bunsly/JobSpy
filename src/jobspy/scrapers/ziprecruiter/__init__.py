"""
jobspy.scrapers.ziprecruiter
~~~~~~~~~~~~~~~~~~~

This module contains routines to scrape ZipRecruiter.
"""
import math
import json
import re
import traceback
from datetime import datetime
from typing import Optional, Tuple
from urllib.parse import urlparse, parse_qs

import tls_client
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from concurrent.futures import ThreadPoolExecutor, Future

from .. import Scraper, ScraperInput, Site
from ..exceptions import ZipRecruiterException
from ...jobs import (
    JobPost,
    Compensation,
    CompensationInterval,
    Location,
    JobResponse,
    JobType,
    Country,
)


class ZipRecruiterScraper(Scraper):
    def __init__(self, proxy: Optional[str] = None):
        """
        Initializes LinkedInScraper with the ZipRecruiter job search url
        """
        site = Site(Site.ZIP_RECRUITER)
        self.url = "https://www.ziprecruiter.com"
        super().__init__(site, proxy=proxy)

        self.jobs_per_page = 20
        self.seen_urls = set()
        self.session = tls_client.Session(
            client_identifier="chrome112", random_tls_extension_order=True
        )

    def find_jobs_in_page(
        self, scraper_input: ScraperInput, page: int
    ) -> tuple[list[JobPost], int | None]:
        """
        Scrapes a page of ZipRecruiter for jobs with scraper_input criteria
        :param scraper_input:
        :param page:
        :param session:
        :return: jobs found on page, total number of jobs found for search
        """
        job_list: list[JobPost] = []
        try:
            response = self.session.get(
                self.url + "/jobs-search",
                headers=ZipRecruiterScraper.headers(),
                params=ZipRecruiterScraper.add_params(scraper_input, page),
                allow_redirects=True,
                proxy=self.proxy,
                timeout_seconds=10,
            )
            if response.status_code != 200:
                raise ZipRecruiterException(
                    f"bad response status code: {response.status_code}"
                )
        except Exception as e:
            if "Proxy responded with non 200 code" in str(e):
                raise ZipRecruiterException("bad proxy")
            raise ZipRecruiterException(str(e))
        else:
            soup = BeautifulSoup(response.text, "html.parser")
            js_tag = soup.find("script", {"id": "js_variables"})

        if js_tag:
            page_json = json.loads(js_tag.string)
            jobs_list = page_json.get("jobList")
            if jobs_list:
                page_variant = "javascript"
                # print('type javascript', len(jobs_list))
            else:
                page_variant = "html_2"
                jobs_list = soup.find_all("div", {"class": "job_content"})
                # print('type 2 html', len(jobs_list))
        else:
            page_variant = "html_1"
            jobs_list = soup.find_all("li", {"class": "job-listing"})
            # print('type 1 html', len(jobs_list))
            # with open("zip_method_8.html", "w") as f:
            #     f.write(soup.prettify())

        with ThreadPoolExecutor(max_workers=10) as executor:
            if page_variant == "javascript":
                job_results = [
                    executor.submit(self.process_job_javascript, job)
                    for job in jobs_list
                ]
            elif page_variant == "html_1":
                job_results = [
                    executor.submit(self.process_job_html_1, job) for job in jobs_list
                ]
            elif page_variant == "html_2":
                job_results = [
                    executor.submit(self.process_job_html_2, job) for job in jobs_list
                ]

        job_list = [result.result() for result in job_results if result.result()]
        return job_list

    def scrape(self, scraper_input: ScraperInput) -> JobResponse:
        """
        Scrapes ZipRecruiter for jobs with scraper_input criteria
        :param scraper_input:
        :return: job_response
        """
        #: get first page to initialize session
        job_list: list[JobPost] = self.find_jobs_in_page(scraper_input, 1)
        pages_to_process = max(
            3, math.ceil(scraper_input.results_wanted / self.jobs_per_page)
        )

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures: list[Future] = [
                executor.submit(self.find_jobs_in_page, scraper_input, page)
                for page in range(2, pages_to_process + 1)
            ]

            for future in futures:
                jobs = future.result()

                job_list += jobs

        job_list = job_list[: scraper_input.results_wanted]
        return JobResponse(jobs=job_list)

    def process_job_html_1(self, job: Tag) -> Optional[JobPost]:
        """
        Parses a job from the job content tag
        :param job: BeautifulSoup Tag for one job post
        :return JobPost
        """
        job_url = job.find("a", {"class": "job_link"})["href"]
        if job_url in self.seen_urls:
            return None

        title = job.find("h2", {"class": "title"}).text
        company = job.find("a", {"class": "company_name"}).text.strip()

        description, updated_job_url = self.get_description(job_url)
        job_url = updated_job_url if updated_job_url else job_url
        if description is None:
            description = job.find("p", {"class": "job_snippet"}).text.strip()

        job_type_element = job.find("li", {"class": "perk_item perk_type"})
        job_type = None
        if job_type_element:
            job_type_text = (
                job_type_element.text.strip().lower().replace("_", "").replace(" ", "")
            )
            job_type = ZipRecruiterScraper.get_job_type_enum(job_type_text)

        date_posted = ZipRecruiterScraper.get_date_posted(job)

        job_post = JobPost(
            title=title,
            description=description,
            company_name=company,
            location=ZipRecruiterScraper.get_location(job),
            job_type=job_type,
            compensation=ZipRecruiterScraper.get_compensation(job),
            date_posted=date_posted,
            job_url=job_url,
        )
        return job_post

    def process_job_html_2(self, job: Tag) -> Optional[JobPost]:
        """
        Parses a job from the job content tag for a second variat of HTML that ZR uses
        :param job: BeautifulSoup Tag for one job post
        :return JobPost
        """
        job_url = job.find("a", class_="job_link")["href"]
        title = job.find("h2", class_="title").text
        company = job.find("a", class_="company_name").text.strip()

        description, updated_job_url = self.get_description(job_url)
        job_url = updated_job_url if updated_job_url else job_url
        if description is None:
            description = job.find("p", class_="job_snippet").get_text().strip()

        job_type_text = job.find("li", class_="perk_item perk_type")
        job_type = None
        if job_type_text:
            job_type_text = (
                job_type_text.get_text()
                .strip()
                .lower()
                .replace("-", "")
                .replace(" ", "")
            )
            job_type = ZipRecruiterScraper.get_job_type_enum(job_type_text)
        date_posted = ZipRecruiterScraper.get_date_posted(job)

        job_post = JobPost(
            title=title,
            description=description,
            company_name=company,
            location=ZipRecruiterScraper.get_location(job),
            job_type=job_type,
            compensation=ZipRecruiterScraper.get_compensation(job),
            date_posted=date_posted,
            job_url=job_url,
        )
        return job_post

    def process_job_javascript(self, job: dict) -> JobPost:
        title = job.get("Title")
        job_url = job.get("JobURL")

        description, updated_job_url = self.get_description(job_url)
        job_url = updated_job_url if updated_job_url else job_url
        if description is None:
            description = BeautifulSoup(
                job.get("Snippet", "").strip(), "html.parser"
            ).get_text()

        company = job.get("OrgName")
        location = Location(
            city=job.get("City"), state=job.get("State"), country=Country.US_CANADA
        )
        job_type = ZipRecruiterScraper.get_job_type_enum(
            job.get("EmploymentType", "").replace("-", "").lower()
        )

        formatted_salary = job.get("FormattedSalaryShort", "")
        salary_parts = formatted_salary.split(" ")

        min_salary_str = salary_parts[0][1:].replace(",", "")
        if "." in min_salary_str:
            min_amount = int(float(min_salary_str) * 1000)
        else:
            min_amount = int(min_salary_str.replace("K", "000"))

        if len(salary_parts) >= 3 and salary_parts[2].startswith("$"):
            max_salary_str = salary_parts[2][1:].replace(",", "")
            if "." in max_salary_str:
                max_amount = int(float(max_salary_str) * 1000)
            else:
                max_amount = int(max_salary_str.replace("K", "000"))
        else:
            max_amount = 0

        compensation = Compensation(
            interval=CompensationInterval.YEARLY,
            min_amount=min_amount,
            max_amount=max_amount,
            currency="USD/CAD",
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
        job_url = job.get("JobURL")

        return JobPost(
            title=title,
            description=description,
            company_name=company,
            location=location,
            job_type=job_type,
            compensation=compensation,
            date_posted=date_posted,
            job_url=job_url,
        )
        return job_post

    @staticmethod
    def get_job_type_enum(job_type_str: str) -> Optional[JobType]:
        for job_type in JobType:
            if job_type_str in job_type.value:
                a = True
                return job_type
        return None

    def get_description(self, job_page_url: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Retrieves job description by going to the job page url
        :param job_page_url:
        :param session:
        :return: description or None, response url
        """
        try:
            response = requests.get(
                job_page_url,
                headers=ZipRecruiterScraper.headers(),
                allow_redirects=True,
                timeout=5,
                proxies=self.proxy,
            )
            if response.status_code not in range(200, 400):
                return None, None
        except Exception as e:
            return None, None

        html_string = response.content
        soup_job = BeautifulSoup(html_string, "html.parser")

        job_description_div = soup_job.find("div", {"class": "job_description"})
        if job_description_div:
            return job_description_div.text.strip(), response.url
        return None, response.url

    @staticmethod
    def add_params(scraper_input, page) -> Optional[str]:
        params = {
            "search": scraper_input.search_term,
            "location": scraper_input.location,
            "page": page,
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
    def get_interval(interval_str: str):
        """
         Maps the interval alias to its appropriate CompensationInterval.
        :param interval_str
        :return: CompensationInterval
        """
        interval_alias = {"annually": CompensationInterval.YEARLY}
        interval_str = interval_str.lower()

        if interval_str in interval_alias:
            return interval_alias[interval_str]

        return CompensationInterval(interval_str)

    @staticmethod
    def get_date_posted(job: BeautifulSoup) -> Optional[datetime.date]:
        """
        Extracts the date a job was posted
        :param job
        :return: date the job was posted or None
        """
        button = job.find(
            "button", {"class": "action_input save_job zrs_btn_secondary_200"}
        )
        if not button:
            return None

        url_time = button.get("data-href", "")
        url_components = urlparse(url_time)
        params = parse_qs(url_components.query)
        posted_time_str = params.get("posted_time", [None])[0]

        if posted_time_str:
            posted_date = datetime.strptime(
                posted_time_str, "%Y-%m-%dT%H:%M:%SZ"
            ).date()
            return posted_date

        return None

    @staticmethod
    def get_compensation(job: BeautifulSoup) -> Optional[Compensation]:
        """
        Parses the compensation tag from the job BeautifulSoup object
        :param job
        :return: Compensation object or None
        """
        pay_element = job.find("li", {"class": "perk_item perk_pay"})
        if pay_element is None:
            return None
        pay = pay_element.find("div", {"class": "value"}).find("span").text.strip()

        def create_compensation_object(pay_string: str) -> Compensation:
            """
            Creates a Compensation object from a pay_string
            :param pay_string
            :return: compensation
            """
            interval = ZipRecruiterScraper.get_interval(pay_string.split()[-1])

            amounts = []
            for amount in pay_string.split("to"):
                amount = amount.replace(",", "").strip("$ ").split(" ")[0]
                if "K" in amount:
                    amount = amount.replace("K", "")
                    amount = int(float(amount)) * 1000
                else:
                    amount = int(float(amount))
                amounts.append(amount)

            compensation = Compensation(
                interval=interval,
                min_amount=min(amounts),
                max_amount=max(amounts),
                currency="USD/CAD",
            )

            return compensation

        return create_compensation_object(pay)

    @staticmethod
    def get_location(job: BeautifulSoup) -> Location:
        """
        Extracts the job location from BeatifulSoup object
        :param job:
        :return: location
        """
        location_link = job.find("a", {"class": "company_location"})
        if location_link is not None:
            location_string = location_link.text.strip()
            parts = location_string.split(", ")
            if len(parts) == 2:
                city, state = parts
            else:
                city, state = None, None
        else:
            city, state = None, None
        return Location(city=city, state=state, country=Country.US_CANADA)

    @staticmethod
    def headers() -> dict:
        """
        Returns headers needed for requests
        :return: dict - Dictionary containing headers
        """
        return {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36"
        }
