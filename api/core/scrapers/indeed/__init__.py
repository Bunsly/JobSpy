import re
import json
from typing import Optional

import tls_client
from bs4 import BeautifulSoup
from bs4.element import Tag
from fastapi import status

from api.core.jobs import *
from api.core.scrapers import Scraper, ScraperInput, Site


class ParsingException(Exception):
    pass


class IndeedScraper(Scraper):
    def __init__(self):
        """
        Initializes IndeedScraper with the Indeed job search url
        """
        site = Site(Site.INDEED)
        super().__init__(site)
        self.url = "https://www.indeed.com/jobs"

    def scrape(self, scraper_input: ScraperInput) -> JobResponse:
        """
        Scrapes Indeed for jobs with scraper_input criteria
        :param scraper_input:
        :return: job_response
        """
        session = tls_client.Session(
            client_identifier="chrome112", random_tls_extension_order=True
        )

        job_list: list[JobPost] = []
        page = 0
        processed_jobs, total_num_jobs = 0, 0
        seen_urls = set()
        while len(job_list) < scraper_input.results_wanted:
            params = {
                "q": scraper_input.search_term,
                "l": scraper_input.location,
                "filter": 0,
                "start": 0 + page * 10,
                "radius": scraper_input.distance,
            }

            response = session.get(self.url, params=params)

            if response.status_code != status.HTTP_200_OK:
                return JobResponse(
                    success=False,
                    error=f"Response returned {response.status_code}",
                )

            soup = BeautifulSoup(response.content, "html.parser")

            try:
                jobs = IndeedScraper.parse_jobs(soup)
            except ParsingException:
                return JobResponse(
                    success=False,
                    error="Failed to parse jobs.",
                )

            total_num_jobs = IndeedScraper.total_jobs(soup)

            if (
                not jobs.get("metaData", {})
                .get("mosaicProviderJobCardsModel", {})
                .get("results")
            ):
                return JobResponse(
                    success=False,
                    error="No jobs found",
                )

            for job in jobs["metaData"]["mosaicProviderJobCardsModel"]["results"]:
                job_url = job["thirdPartyApplyUrl"]
                if job_url in seen_urls:
                    continue
                snippet_html = BeautifulSoup(job["snippet"], "html.parser")

                extracted_salary = job.get("extractedSalary")
                compensation = None
                if extracted_salary:
                    salary_snippet = job.get("salarySnippet")
                    currency = (
                        salary_snippet.get("currency") if salary_snippet else None
                    )
                    interval = (extracted_salary.get("type"),)
                    if isinstance(interval, tuple):
                        interval = interval[0]

                    interval = interval.upper()
                    if interval in CompensationInterval.__members__:
                        compensation = Compensation(
                            interval=CompensationInterval[interval],
                            min_amount=extracted_salary.get("max"),
                            max_amount=extracted_salary.get("min"),
                            currency=currency,
                        )

                job_type = IndeedScraper.get_job_type(job)
                if job.get("thirdPartyApplyUrl"):
                    delivery = Delivery(method=DeliveryEnum.URL, value=job_url)
                else:
                    delivery = None
                timestamp_seconds = job["pubDate"] / 1000
                date_posted = datetime.fromtimestamp(timestamp_seconds)

                first_li = snippet_html.find("li")
                job_post = JobPost(
                    title=job["normTitle"],
                    description=first_li.text if first_li else None,
                    company_name=job["company"],
                    location=Location(
                        city=job["jobLocationCity"],
                        state=job["jobLocationState"],
                        postal_code=job.get("jobLocationPostal"),
                        country="US",
                    ),
                    job_type=job_type,
                    compensation=compensation,
                    date_posted=date_posted,
                    delivery=delivery,
                )
                job_list.append(job_post)
                if len(job_list) >= scraper_input.results_wanted:
                    break

            if (
                len(job_list) >= scraper_input.results_wanted
                or processed_jobs >= total_num_jobs
            ):
                break
            page += 1

        job_list = job_list[: scraper_input.results_wanted]
        job_response = JobResponse(
            success=True,
            jobs=job_list,
            job_count=total_num_jobs,
        )
        return job_response

    @staticmethod
    def get_job_type(job: dict) -> Optional[JobType]:
        """
        Parses the job to get JobType
        :param job:
        :return:
        """
        for taxonomy in job["taxonomyAttributes"]:
            if taxonomy["label"] == "job-types":
                if len(taxonomy["attributes"]) > 0:
                    job_type_str = (
                        taxonomy["attributes"][0]["label"]
                        .replace("-", "_")
                        .replace(" ", "_")
                        .upper()
                    )
                    return JobType[job_type_str]
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
                raise ParsingException("Could not find mosaic provider job cards data")
        else:
            raise ParsingException(
                "Could not find a script tag containing mosaic provider data"
            )

    @staticmethod
    def total_jobs(soup: BeautifulSoup) -> int:
        """
        Parses the total jobs for that search from soup object
        :param soup:
        :return: total_num_jobs
        """
        script = soup.find("script", string=lambda t: "window._initialData" in t)

        pattern = re.compile(r"window._initialData\s*=\s*({.*})\s*;", re.DOTALL)
        match = pattern.search(script.string)
        total_num_jobs = 0
        if match:
            json_str = match.group(1)
            data = json.loads(json_str)
            total_num_jobs = int(data["searchTitleBarModel"]["totalNumResults"])
        return total_num_jobs
