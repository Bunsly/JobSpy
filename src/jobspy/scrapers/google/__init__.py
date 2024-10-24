"""
jobspy.scrapers.google
~~~~~~~~~~~~~~~~~~~

This module contains routines to scrape Google.
"""

from __future__ import annotations

import math
import re
import json
from typing import Tuple
from datetime import datetime, timedelta

from .constants import headers_jobs, headers_initial, async_param
from .. import Scraper, ScraperInput, Site
from ..utils import extract_emails_from_text, create_logger, extract_job_type
from ..utils import (
    create_session,
)
from ...jobs import (
    JobPost,
    JobResponse,
    Location,
    JobType,
)

logger = create_logger("Google")


class GoogleJobsScraper(Scraper):
    def __init__(
        self, proxies: list[str] | str | None = None, ca_cert: str | None = None
    ):
        """
        Initializes Google Scraper with the Goodle jobs search url
        """
        site = Site(Site.GOOGLE)
        super().__init__(site, proxies=proxies, ca_cert=ca_cert)

        self.country = None
        self.session = None
        self.scraper_input = None
        self.jobs_per_page = 10
        self.seen_urls = set()
        self.url = "https://www.google.com/search"
        self.jobs_url = "https://www.google.com/async/callback:550"

    def scrape(self, scraper_input: ScraperInput) -> JobResponse:
        """
        Scrapes Google for jobs with scraper_input criteria.
        :param scraper_input: Information about job search criteria.
        :return: JobResponse containing a list of jobs.
        """
        self.scraper_input = scraper_input
        self.scraper_input.results_wanted = min(900, scraper_input.results_wanted)

        self.session = create_session(
            proxies=self.proxies, ca_cert=self.ca_cert, is_tls=False, has_retry=True
        )
        forward_cursor = self._get_initial_cursor()
        if forward_cursor is None:
            logger.error("initial cursor not found")
            return JobResponse(jobs=[])

        page = 1
        job_list: list[JobPost] = []

        while (
            len(self.seen_urls) < scraper_input.results_wanted + scraper_input.offset
            and forward_cursor
        ):
            logger.info(
                f"search page: {page} / {math.ceil(scraper_input.results_wanted / self.jobs_per_page)}"
            )
            jobs, forward_cursor = self._get_jobs_next_page(forward_cursor)
            if not jobs:
                logger.info(f"found no jobs on page: {page}")
                break
            job_list += jobs
            page += 1
        return JobResponse(
            jobs=job_list[
                scraper_input.offset : scraper_input.offset
                + scraper_input.results_wanted
            ]
        )

    def _get_initial_cursor(self):
        """Gets initial cursor to paginate through job listings"""
        query = f"{self.scraper_input.search_term} jobs"

        def get_time_range(hours_old):
            if hours_old <= 24:
                return "since yesterday"
            elif hours_old <= 72:
                return "in the last 3 days"
            elif hours_old <= 168:
                return "in the last week"
            else:
                return "in the last month"

        job_type_mapping = {
            JobType.FULL_TIME: "Full time",
            JobType.PART_TIME: "Part time",
            JobType.INTERNSHIP: "Internship",
            JobType.CONTRACT: "Contract",
        }

        if self.scraper_input.job_type in job_type_mapping:
            query += f" {job_type_mapping[self.scraper_input.job_type]}"

        if self.scraper_input.location:
            query += f" near {self.scraper_input.location}"

        if self.scraper_input.hours_old:
            time_filter = get_time_range(self.scraper_input.hours_old)
            query += f" {time_filter}"

        if self.scraper_input.is_remote:
            query += " remote"

        params = {"q": query, "udm": "8"}
        response = self.session.get(self.url, headers=headers_initial, params=params)

        pattern_fc = r'<div jsname="Yust4d"[^>]+data-async-fc="([^"]+)"'
        match_fc = re.search(pattern_fc, response.text)
        data_async_fc = match_fc.group(1) if match_fc else None
        return data_async_fc

    def _get_jobs_next_page(self, forward_cursor: str) -> Tuple[list[JobPost], str]:
        params = {"fc": [forward_cursor], "fcv": ["3"], "async": [async_param]}
        response = self.session.get(self.jobs_url, headers=headers_jobs, params=params)
        return self._parse_jobs(response.text)

    def _parse_jobs(self, job_data: str) -> Tuple[list[JobPost], str]:
        """
        Parses jobs on a page with next page cursor
        """
        start_idx = job_data.find("[[[")
        end_idx = job_data.rindex("]]]") + 3
        s = job_data[start_idx:end_idx]
        parsed = json.loads(s)[0]

        pattern_fc = r'data-async-fc="([^"]+)"'
        match_fc = re.search(pattern_fc, job_data)
        data_async_fc = match_fc.group(1) if match_fc else None
        jobs_on_page = []

        for array in parsed:

            _, job_data = array
            if not job_data.startswith("[[["):
                continue
            job_d = json.loads(job_data)

            job_info = self._find_job_info(job_d)

            job_url = job_info[3][0][0] if job_info[3] and job_info[3][0] else None
            if job_url in self.seen_urls:
                continue
            self.seen_urls.add(job_url)

            title = job_info[0]
            company_name = job_info[1]
            location = city = job_info[2]
            state = country = date_posted = None
            if location and "," in location:
                city, state, *country = [*map(lambda x: x.strip(), location.split(","))]

            days_ago_str = job_info[12]
            if type(days_ago_str) == str:
                match = re.search(r"\d+", days_ago_str)
                days_ago = int(match.group()) if match else None
                date_posted = (datetime.now() - timedelta(days=days_ago)).date()

            description = job_info[19]

            job_post = JobPost(
                id=f"go-{job_info[28]}",
                title=title,
                company_name=company_name,
                location=Location(
                    city=city, state=state, country=country[0] if country else None
                ),
                job_url=job_url,
                job_url_direct=job_url,
                date_posted=date_posted,
                is_remote="remote" in description.lower()
                or "wfh" in description.lower(),
                description=description,
                emails=extract_emails_from_text(description),
                job_type=extract_job_type(description),
            )
            jobs_on_page.append(job_post)
        return jobs_on_page, data_async_fc

    @staticmethod
    def _find_job_info(jobs_data: list | dict) -> list | None:
        """Iterates through the JSON data to find the job listings"""
        if isinstance(jobs_data, dict):
            for key, value in jobs_data.items():
                if key == "520084652" and isinstance(value, list):
                    return value
                else:
                    result = GoogleJobsScraper._find_job_info(value)
                    if result:
                        return result
        elif isinstance(jobs_data, list):
            for item in jobs_data:
                result = GoogleJobsScraper._find_job_info(item)
                if result:
                    return result
        return None
