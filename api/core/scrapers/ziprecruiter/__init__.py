import json
from typing import Optional, Tuple, List
from urllib.parse import urlparse, parse_qs

import tls_client
from fastapi import status
from bs4 import BeautifulSoup
from bs4.element import Tag
from concurrent.futures import ThreadPoolExecutor, Future

from api.core.jobs import JobPost
from api.core.scrapers import Scraper, ScraperInput, Site, StatusException
from api.core.jobs import *
import math


class ZipRecruiterScraper(Scraper):
    def __init__(self):
        """
        Initializes LinkedInScraper with the ZipRecruiter job search url
        """
        site = Site(Site.ZIP_RECRUITER)
        url = "https://www.ziprecruiter.com"
        super().__init__(site, url)

        self.jobs_per_page = 20
        self.seen_urls = set()

    def scrape_page(
        self, scraper_input: ScraperInput, page: int, session: tls_client.Session
    ) -> tuple[list[JobPost], int | None]:
        """
        Scrapes a page of ZipRecruiter for jobs with scraper_input criteria
        :param scraper_input:
        :param page:
        :param session:
        :return: jobs found on page, total number of jobs found for search
        """

        job_list = []

        job_type_value = None
        if scraper_input.job_type:
            if scraper_input.job_type.value == "fulltime":
                job_type_value = "full_time"
            elif scraper_input.job_type.value == "parttime":
                job_type_value = "part_time"
            else:
                job_type_value = scraper_input.job_type.value

        params = {
            "search": scraper_input.search_term,
            "location": scraper_input.location,
            "radius": scraper_input.distance,
            "refine_by_location_type": "only_remote"
            if scraper_input.is_remote
            else None,
            "refine_by_employment": f"employment_type:employment_type:{job_type_value}"
            if job_type_value
            else None,
            "page": page,
        }

        response = session.get(
            self.url + "/jobs-search",
            headers=ZipRecruiterScraper.headers(),
            params=params,
        )

        if response.status_code != status.HTTP_200_OK:
            raise StatusException(response.status_code)

        html_string = response.content
        soup = BeautifulSoup(html_string, "html.parser")

        if page == 1:
            script_tag = soup.find("script", {"id": "js_variables"})
            data = json.loads(script_tag.string)

            job_count = int(data["totalJobCount"].replace(",", ""))
        else:
            job_count = None

        job_posts = soup.find_all("div", {"class": "job_content"})

        def process_job(job: Tag) -> Optional[JobPost]:
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

            description, updated_job_url = ZipRecruiterScraper.get_description(job_url, session)
            if updated_job_url is not None:
                job_url = updated_job_url
            if description is None:
                description = job.find("p", {"class": "job_snippet"}).text.strip()

            job_type_element = job.find("li", {"class": "perk_item perk_type"})
            if job_type_element:
                job_type_text = (
                    job_type_element.text.strip()
                    .lower()
                    .replace("-", "")
                    .replace(" ", "")
                )
                if job_type_text == "contractor":
                    job_type_text = "contract"
                job_type = JobType(job_type_text)
            else:
                job_type = None

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

        with ThreadPoolExecutor(max_workers=10) as executor:
            job_results: list[Future] = [
                executor.submit(process_job, job) for job in job_posts
            ]

        job_list = [result.result() for result in job_results if result.result()]

        return job_list, job_count

    def scrape(self, scraper_input: ScraperInput) -> JobResponse:
        """
        Scrapes ZipRecruiter for jobs with scraper_input criteria
        :param scraper_input:
        :return: job_response
        """
        session = tls_client.Session(
            client_identifier="chrome112", random_tls_extension_order=True
        )

        pages_to_process = math.ceil(scraper_input.results_wanted / self.jobs_per_page)

        try:
            #: get first page to initialize session
            job_list, total_results = self.scrape_page(scraper_input, 1, session)

            with ThreadPoolExecutor(max_workers=10) as executor:
                futures: list[Future] = [
                    executor.submit(self.scrape_page, scraper_input, page, session)
                    for page in range(2, pages_to_process + 1)
                ]

                for future in futures:
                    jobs, _ = future.result()

                    job_list += jobs

        except StatusException as e:
            return JobResponse(
                success=False,
                error=f"ZipRecruiter returned status code {e.status_code}",
            )

        #: note: this does not handle if the results are more or less than the results_wanted

        if len(job_list) > scraper_input.results_wanted:
            job_list = job_list[: scraper_input.results_wanted]

        job_response = JobResponse(
            success=True,
            jobs=job_list,
            total_results=total_results,
        )
        return job_response

    @staticmethod
    def get_description(
        job_page_url: str, session: tls_client.Session
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Retrieves job description by going to the job page url
        :param job_page_url:
        :param session:
        :return: description or None, response url
        """
        response = session.get(
            job_page_url, headers=ZipRecruiterScraper.headers(), allow_redirects=True
        )
        if response.status_code not in range(200, 400):
            return None, None

        html_string = response.content
        soup_job = BeautifulSoup(html_string, "html.parser")

        job_description_div = soup_job.find("div", {"class": "job_description"})
        if job_description_div:
            return job_description_div.text.strip(), response.url
        return None, response.url

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
    def get_date_posted(job: BeautifulSoup) -> Optional[str]:
        """
        Extracts the date a job was posted
        :param job
        :return: date the job was posted or None
        """
        button = job.find(
            "button", {"class": "action_input save_job zrs_btn_secondary_200"}
        )
        url_time = button["data-href"]
        url_components = urlparse(url_time)
        params = parse_qs(url_components.query)
        return params.get("posted_time", [None])[0]

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
                    amount = float(amount) * 1000
                else:
                    amount = float(amount)
                amounts.append(amount)

            compensation = Compensation(
                interval=interval, min_amount=min(amounts), max_amount=max(amounts)
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
        return Location(
            city=city,
            state=state,
        )

    @staticmethod
    def headers() -> dict:
        """
        Returns headers needed for requests
        :return: dict - Dictionary containing headers
        """
        return {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36"
        }
