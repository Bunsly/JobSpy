"""
jobspy.scrapers.indeed
~~~~~~~~~~~~~~~~~~~

This module contains routines to scrape Indeed.
"""
import re
import math
import io
import json
import traceback
from datetime import datetime
from typing import Optional

import tls_client
import urllib.parse
from bs4 import BeautifulSoup
from bs4.element import Tag
from concurrent.futures import ThreadPoolExecutor, Future

from ..exceptions import IndeedException
from ...jobs import (
    JobPost,
    Compensation,
    CompensationInterval,
    Location,
    JobResponse,
    JobType,
)
from .. import Scraper, ScraperInput, Site, Country


class IndeedScraper(Scraper):
    def __init__(self, proxy: Optional[str] = None):
        """
        Initializes IndeedScraper with the Indeed job search url
        """
        site = Site(Site.INDEED)
        super().__init__(site, proxy=proxy)

        self.jobs_per_page = 15
        self.seen_urls = set()

    def scrape_page(
        self, scraper_input: ScraperInput, page: int, session: tls_client.Session
    ) -> tuple[list[JobPost], int]:
        """
        Scrapes a page of Indeed for jobs with scraper_input criteria
        :param scraper_input:
        :param page:
        :param session:
        :return: jobs found on page, total number of jobs found for search
        """
        self.country = scraper_input.country
        domain = self.country.domain_value
        self.url = f"https://{domain}.indeed.com"

        job_list: list[JobPost] = []

        params = {
            "q": scraper_input.search_term,
            "l": scraper_input.location,
            "filter": 0,
            "start": 0 + page * 10,
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
        try:
            response = session.get(
                self.url + "/jobs",
                params=params,
                allow_redirects=True,
                proxy=self.proxy,
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

        def process_job(job) -> Optional[JobPost]:
            job_url = f'{self.url}/jobs/viewjob?jk={job["jobkey"]}'
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
                        min_amount=int(extracted_salary.get("max")),
                        max_amount=int(extracted_salary.get("min")),
                        currency=currency,
                    )

            job_type = IndeedScraper.get_job_type(job)
            timestamp_seconds = job["pubDate"] / 1000
            date_posted = datetime.fromtimestamp(timestamp_seconds)
            date_posted = date_posted.strftime("%Y-%m-%d")

            description = self.get_description(job_url, session)
            with io.StringIO(job["snippet"]) as f:
                soup = BeautifulSoup(f, "html.parser")
                li_elements = soup.find_all("li")
                if description is None and li_elements:
                    description = " ".join(li.text for li in li_elements)

            job_post = JobPost(
                title=job["normTitle"],
                description=description,
                company_name=job["company"],
                location=Location(
                    city=job.get("jobLocationCity"),
                    state=job.get("jobLocationState"),
                    country=self.country,
                ),
                job_type=job_type,
                compensation=compensation,
                date_posted=date_posted,
                job_url=job_url_client,
            )
            return job_post

        with ThreadPoolExecutor(max_workers=1) as executor:
            job_results: list[Future] = [
                executor.submit(process_job, job)
                for job in jobs["metaData"]["mosaicProviderJobCardsModel"]["results"]
            ]

        job_list = [result.result() for result in job_results if result.result()]

        return job_list, total_num_jobs

    def scrape(self, scraper_input: ScraperInput) -> JobResponse:
        """
        Scrapes Indeed for jobs with scraper_input criteria
        :param scraper_input:
        :return: job_response
        """
        session = tls_client.Session(
            client_identifier="chrome112", random_tls_extension_order=True
        )

        pages_to_process = (
            math.ceil(scraper_input.results_wanted / self.jobs_per_page) - 1
        )

        #: get first page to initialize session
        job_list, total_results = self.scrape_page(scraper_input, 0, session)

        with ThreadPoolExecutor(max_workers=1) as executor:
            futures: list[Future] = [
                executor.submit(self.scrape_page, scraper_input, page, session)
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

    def get_description(self, job_page_url: str, session: tls_client.Session) -> str:
        """
        Retrieves job description by going to the job page url
        :param job_page_url:
        :param session:
        :return: description
        """
        parsed_url = urllib.parse.urlparse(job_page_url)
        params = urllib.parse.parse_qs(parsed_url.query)
        jk_value = params.get("jk", [None])[0]
        formatted_url = f"{self.url}/viewjob?jk={jk_value}&spa=1"

        try:
            response = session.get(
                formatted_url, allow_redirects=True, timeout_seconds=5, proxy=self.proxy
            )
        except Exception as e:
            return None

        if response.status_code not in range(200, 400):
            return None

        raw_description = response.json()["body"]["jobInfoWrapperModel"][
            "jobInfoModel"
        ]["sanitizedJobDescription"]
        with io.StringIO(raw_description) as f:
            soup = BeautifulSoup(f, "html.parser")
            text_content = " ".join(soup.get_text().split()).strip()
            return text_content

    @staticmethod
    def get_job_type(job: dict) -> Optional[JobType]:
        """
        Parses the job to get JobTypeIndeed
        :param job:
        :return:
        """
        for taxonomy in job["taxonomyAttributes"]:
            if taxonomy["label"] == "job-types":
                if len(taxonomy["attributes"]) > 0:
                    label = taxonomy["attributes"][0].get("label")
                    if label:
                        job_type_str = label.replace("-", "").replace(" ", "").lower()
                        return IndeedScraper.get_enum_from_value(job_type_str)
        return None

    @staticmethod
    def get_enum_from_value(value_str):
        for job_type in JobType:
            if value_str in job_type.value:
                return job_type
        return None

    @staticmethod
    def parse_jobs(soup: BeautifulSoup) -> dict:
        """
        Parses the jobs from the soup object
        :param soup:
        :return: jobs
        """

        def find_mosaic_script() -> Optional[Tag]:
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
                "Could not find a script tag containing mosaic provider data"
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
