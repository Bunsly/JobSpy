"""
jobspy.scrapers.indeed
~~~~~~~~~~~~~~~~~~~

This module contains routines to scrape Indeed.
"""
import re
import math
import io
import json
from typing import Any
from datetime import datetime

import urllib.parse
from bs4 import BeautifulSoup
from bs4.element import Tag
from concurrent.futures import ThreadPoolExecutor, Future

from ..exceptions import IndeedException
from ..utils import (
    count_urgent_words,
    extract_emails_from_text,
    create_session,
    get_enum_from_job_type,
    modify_and_get_description
)
from ...jobs import (
    JobPost,
    Compensation,
    CompensationInterval,
    Location,
    JobResponse,
    JobType,
)
from .. import Scraper, ScraperInput, Site


class IndeedScraper(Scraper):
    def __init__(self, proxy: str | None = None):
        """
        Initializes IndeedScraper with the Indeed job search url
        """
        self.url = None
        self.country = None
        site = Site(Site.INDEED)
        super().__init__(site, proxy=proxy)

        self.jobs_per_page = 25
        self.seen_urls = set()

    def scrape_page(
        self, scraper_input: ScraperInput, page: int
    ) -> tuple[list[JobPost], int]:
        """
        Scrapes a page of Indeed for jobs with scraper_input criteria
        :param scraper_input:
        :param page:
        :return: jobs found on page, total number of jobs found for search
        """
        self.country = scraper_input.country
        domain = self.country.indeed_domain_value
        self.url = f"https://{domain}.indeed.com"

        try:
            session = create_session(self.proxy)
            response = session.get(
                f"{self.url}/m/jobs",
                headers=self.get_headers(),
                params=self.add_params(scraper_input, page),
                allow_redirects=True,
                timeout_seconds=10,
            )
            if response.status_code not in range(200, 400):
                raise IndeedException(
                    f"bad response with status code: {response.status_code}"
                )
        except Exception as e:
            if "Proxy responded with" in str(e):
                raise IndeedException("bad proxy")
            raise IndeedException(str(e))

        soup = BeautifulSoup(response.content, "html.parser")
        if "did not match any jobs" in response.text:
            raise IndeedException("Parsing exception: Search did not match any jobs")

        jobs = IndeedScraper.parse_jobs(
            soup
        )  #: can raise exception, handled by main scrape function
        total_num_jobs = IndeedScraper.total_jobs(soup)

        if (
            not jobs.get("metaData", {})
            .get("mosaicProviderJobCardsModel", {})
            .get("results")
        ):
            raise IndeedException("No jobs found.")

        def process_job(job: dict) -> JobPost | None:
            job_url = f'{self.url}/m/jobs/viewjob?jk={job["jobkey"]}'
            job_url_client = f'{self.url}/viewjob?jk={job["jobkey"]}'
            if job_url in self.seen_urls:
                return None

            extracted_salary = job.get("extractedSalary")
            compensation = None
            if extracted_salary:
                salary_snippet = job.get("salarySnippet")
                currency = salary_snippet.get("currency") if salary_snippet else None
                interval = (extracted_salary.get("type"),)
                if isinstance(interval, tuple):
                    interval = interval[0]

                interval = interval.upper()
                if interval in CompensationInterval.__members__:
                    compensation = Compensation(
                        interval=CompensationInterval[interval],
                        min_amount=int(extracted_salary.get("min")),
                        max_amount=int(extracted_salary.get("max")),
                        currency=currency,
                    )

            job_type = IndeedScraper.get_job_type(job)
            timestamp_seconds = job["pubDate"] / 1000
            date_posted = datetime.fromtimestamp(timestamp_seconds)
            date_posted = date_posted.strftime("%Y-%m-%d")

            description = self.get_description(job_url) if scraper_input.full_description else None

            with io.StringIO(job["snippet"]) as f:
                soup_io = BeautifulSoup(f, "html.parser")
                li_elements = soup_io.find_all("li")
                if description is None and li_elements:
                    description = " ".join(li.text for li in li_elements)

            job_post = JobPost(
                title=job["normTitle"],
                description=description,
                company_name=job["company"],
                company_url=self.url + job["companyOverviewLink"] if "companyOverviewLink" in job else None,
                location=Location(
                    city=job.get("jobLocationCity"),
                    state=job.get("jobLocationState"),
                    country=self.country,
                ),
                job_type=job_type,
                compensation=compensation,
                date_posted=date_posted,
                job_url=job_url_client,
                emails=extract_emails_from_text(description) if description else None,
                num_urgent_words=count_urgent_words(description)
                if description
                else None,
                is_remote=self.is_remote_job(job),
            )
            return job_post

        workers = 10 if scraper_input.full_description else 10  # possibly lessen 10 when fetching desc based on feedback
        jobs = jobs["metaData"]["mosaicProviderJobCardsModel"]["results"]
        with ThreadPoolExecutor(max_workers=workers) as executor:
            job_results: list[Future] = [
                executor.submit(process_job, job) for job in jobs
            ]

        job_list = [result.result() for result in job_results if result.result()]

        return job_list, total_num_jobs

    def scrape(self, scraper_input: ScraperInput) -> JobResponse:
        """
        Scrapes Indeed for jobs with scraper_input criteria
        :param scraper_input:
        :return: job_response
        """
        pages_to_process = (
            math.ceil(scraper_input.results_wanted / self.jobs_per_page) - 1
        )

        #: get first page to initialize session
        job_list, total_results = self.scrape_page(scraper_input, 0)

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures: list[Future] = [
                executor.submit(self.scrape_page, scraper_input, page)
                for page in range(1, pages_to_process + 1)
            ]

            for future in futures:
                jobs, _ = future.result()

                job_list += jobs

        if len(job_list) > scraper_input.results_wanted:
            job_list = job_list[: scraper_input.results_wanted]

        job_response = JobResponse(
            jobs=job_list,
            total_results=total_results,
        )
        return job_response

    def get_description(self, job_page_url: str) -> str | None:
        """
        Retrieves job description by going to the job page url
        :param job_page_url:
        :return: description
        """
        parsed_url = urllib.parse.urlparse(job_page_url)
        params = urllib.parse.parse_qs(parsed_url.query)
        jk_value = params.get("jk", [None])[0]
        formatted_url = f"{self.url}/m/viewjob?jk={jk_value}&spa=1"
        session = create_session(self.proxy)

        try:
            response = session.get(
                formatted_url,
                headers=self.get_headers(),
                allow_redirects=True,
                timeout_seconds=5,
            )
        except Exception as e:
            return None

        if response.status_code not in range(200, 400):
            return None

        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            script_tags = soup.find_all('script')

            job_description = ''
            for tag in script_tags:
                if 'window._initialData' in tag.text:
                    json_str = tag.text
                    json_str = json_str.split('window._initialData=')[1]
                    json_str = json_str.rsplit(';', 1)[0]
                    data = json.loads(json_str)
                    job_description = data["jobInfoWrapperModel"]["jobInfoModel"]["sanitizedJobDescription"]
                    break
        except (KeyError, TypeError, IndexError):
            return None

        soup = BeautifulSoup(job_description, "html.parser")
        return modify_and_get_description(soup)

    @staticmethod
    def get_job_type(job: dict) -> list[JobType] | None:
        """
        Parses the job to get list of job types
        :param job:
        :return:
        """
        job_types: list[JobType] = []
        for taxonomy in job["taxonomyAttributes"]:
            if taxonomy["label"] == "job-types":
                for i in range(len(taxonomy["attributes"])):
                    label = taxonomy["attributes"][i].get("label")
                    if label:
                        job_type_str = label.replace("-", "").replace(" ", "").lower()
                        job_type = get_enum_from_job_type(job_type_str)
                        if job_type:
                            job_types.append(job_type)
        return job_types

    @staticmethod
    def parse_jobs(soup: BeautifulSoup) -> dict:
        """
        Parses the jobs from the soup object
        :param soup:
        :return: jobs
        """

        def find_mosaic_script() -> Tag | None:
            """
            Finds jobcards script tag
            :return: script_tag
            """
            script_tags = soup.find_all("script")

            for tag in script_tags:
                if (
                    tag.string
                    and "mosaic.providerData" in tag.string
                    and "mosaic-provider-jobcards" in tag.string
                ):
                    return tag
            return None

        script_tag = find_mosaic_script()

        if script_tag:
            script_str = script_tag.string
            pattern = r'window.mosaic.providerData\["mosaic-provider-jobcards"\]\s*=\s*({.*?});'
            p = re.compile(pattern, re.DOTALL)
            m = p.search(script_str)
            if m:
                jobs = json.loads(m.group(1).strip())
                return jobs
            else:
                raise IndeedException("Could not find mosaic provider job cards data")
        else:
            raise IndeedException(
                "Could not find any results for the search"
            )

    @staticmethod
    def total_jobs(soup: BeautifulSoup) -> int:
        """
        Parses the total jobs for that search from soup object
        :param soup:
        :return: total_num_jobs
        """
        script = soup.find("script", string=lambda t: t and "window._initialData" in t)

        pattern = re.compile(r"window._initialData\s*=\s*({.*})\s*;", re.DOTALL)
        match = pattern.search(script.string)
        total_num_jobs = 0
        if match:
            json_str = match.group(1)
            data = json.loads(json_str)
            total_num_jobs = int(data["searchTitleBarModel"]["totalNumResults"])
        return total_num_jobs

    @staticmethod
    def get_headers():
        return {
          'Host': 'www.indeed.com',
          'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
          'sec-fetch-site': 'same-origin',
          'sec-fetch-dest': 'document',
          'accept-language': 'en-US,en;q=0.9',
          'sec-fetch-mode': 'navigate',
          'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Indeed App 192.0',
          'referer': 'https://www.indeed.com/m/jobs?q=software%20intern&l=Dallas%2C%20TX&from=serpso&rq=1&rsIdx=3',
        }

    @staticmethod
    def is_remote_job(job: dict) -> bool:
        """
        :param job:
        :return: bool
        """
        for taxonomy in job.get("taxonomyAttributes", []):
            if taxonomy["label"] == "remote" and len(taxonomy["attributes"]) > 0:
                return True
        return False

    @staticmethod
    def add_params(scraper_input: ScraperInput, page: int) -> dict[str, str | Any]:
        params = {
            "q": scraper_input.search_term,
            "l": scraper_input.location,
            "filter": 0,
            "start": scraper_input.offset + page * 10,
            "sort": "date"
        }
        if scraper_input.distance:
            params["radius"] = scraper_input.distance

        sc_values = []
        if scraper_input.is_remote:
            sc_values.append("attr(DSQF7)")
        if scraper_input.job_type:
            sc_values.append("jt({})".format(scraper_input.job_type.value))

        if sc_values:
            params["sc"] = "0kf:" + "".join(sc_values) + ";"

        if scraper_input.easy_apply:
            params['iafilter'] = 1

        return params
