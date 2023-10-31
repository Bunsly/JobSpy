"""
jobspy.scrapers.indeed
~~~~~~~~~~~~~~~~~~~

This module contains routines to scrape Indeed.
"""
import re
import math
import io
import json
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

        self.jobs_per_page = 15
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

        params = {
            "q": scraper_input.search_term,
            "l": scraper_input.location,
            "filter": 0,
            "start": scraper_input.offset + page * 10,
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
            session = create_session(self.proxy, is_tls=True)
            response = session.get(
                f"{self.url}/jobs",
                headers=self.get_headers(),
                params=params,
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

        def process_job(job) -> JobPost | None:
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
                        min_amount=int(extracted_salary.get("min")),
                        max_amount=int(extracted_salary.get("max")),
                        currency=currency,
                    )

            job_type = IndeedScraper.get_job_type(job)
            timestamp_seconds = job["pubDate"] / 1000
            date_posted = datetime.fromtimestamp(timestamp_seconds)
            date_posted = date_posted.strftime("%Y-%m-%d")

            description = self.get_description(job_url)
            with io.StringIO(job["snippet"]) as f:
                soup_io = BeautifulSoup(f, "html.parser")
                li_elements = soup_io.find_all("li")
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
                emails=extract_emails_from_text(description) if description else None,
                num_urgent_words=count_urgent_words(description)
                if description
                else None,
                is_remote=self.is_remote_job(job),
            )
            return job_post

        jobs = jobs["metaData"]["mosaicProviderJobCardsModel"]["results"]
        with ThreadPoolExecutor(max_workers=1) as executor:
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

        with ThreadPoolExecutor(max_workers=1) as executor:
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
        formatted_url = f"{self.url}/viewjob?jk={jk_value}&spa=1"
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

        soup = BeautifulSoup(response.text, "html.parser")
        script_tag = soup.find(
            "script", text=lambda x: x and "window._initialData" in x
        )

        if not script_tag:
            return None

        script_code = script_tag.string
        match = re.search(r"window\._initialData\s*=\s*({.*?})\s*;", script_code, re.S)

        if not match:
            return None

        json_string = match.group(1)
        data = json.loads(json_string)
        try:
            job_description = data["jobInfoWrapperModel"]["jobInfoModel"][
                "sanitizedJobDescription"
            ]
        except (KeyError, TypeError, IndexError):
            return None

        soup = BeautifulSoup(job_description, "html.parser")
        text_content = " ".join(soup.get_text(separator=" ").split()).strip()

        return text_content

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

    @staticmethod
    def get_headers():
        return {
            "authority": "www.indeed.com",
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "referer": "https://www.indeed.com/viewjob?jk=fe6182337d72c7b1&tk=1hcbfcmd0k62t802&from=serp&vjs=3&advn=8132938064490989&adid=408692607&ad=-6NYlbfkN0A3Osc99MJFDKjquSk4WOGT28ALb_ad4QMtrHreCb9ICg6MiSVy9oDAp3evvOrI7Q-O9qOtQTg1EPbthP9xWtBN2cOuVeHQijxHjHpJC65TjDtftH3AXeINjBvAyDrE8DrRaAXl8LD3Fs1e_xuDHQIssdZ2Mlzcav8m5jHrA0fA64ZaqJV77myldaNlM7-qyQpy4AsJQfvg9iR2MY7qeC5_FnjIgjKIy_lNi9OPMOjGRWXA94CuvC7zC6WeiJmBQCHISl8IOBxf7EdJZlYdtzgae3593TFxbkd6LUwbijAfjax39aAuuCXy3s9C4YgcEP3TwEFGQoTpYu9Pmle-Ae1tHGPgsjxwXkgMm7Cz5mBBdJioglRCj9pssn-1u1blHZM4uL1nK9p1Y6HoFgPUU9xvKQTHjKGdH8d4y4ETyCMoNF4hAIyUaysCKdJKitC8PXoYaWhDqFtSMR4Jys8UPqUV&xkcb=SoDD-_M3JLQfWnQTDh0LbzkdCdPP&xpse=SoBa6_I3JLW9FlWZlB0PbzkdCdPP&sjdu=i6xVERweJM_pVUvgf-MzuaunBTY7G71J5eEX6t4DrDs5EMPQdODrX7Nn-WIPMezoqr5wA_l7Of-3CtoiUawcHw",
            "sec-ch-ua": '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
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
