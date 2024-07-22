"""
jobspy.scrapers.monster
~~~~~~~~~~~~~~~~~~~

This module contains routines to scrape Monster Jobs.
"""

from __future__ import annotations

import json
import math
import uuid

from concurrent.futures import ThreadPoolExecutor

from dateutil.parser import parse

from .. import Scraper, ScraperInput, Site
from ..utils import (
    logger,
    extract_emails_from_text,
    create_session,
    markdown_converter,
)
from ...jobs import (
    JobPost,
    Location,
    JobResponse,
    DescriptionFormat,
)


class MonsterScraper(Scraper):
    base_url = "https://www.monster.com/job-openings/"
    api_url = "https://appsapi.monster.io/profiles-native-apps-app-service/v3/jobs/search?languageTag=en-US&apikey=fLGr7wcNEfMSzTdWygKnhtyNAB7QzXOq"

    def __init__(self, proxies: list[str] | str | None = None):
        """
        Initializes MonsterScraper
        """
        super().__init__(Site.MONSTER, proxies=proxies)

        self.scraper_input = None
        self.session = create_session(proxies=proxies)
        # self.search_id = "0979dd0c-9886-45ac-b7e3-9395f74f775"
        # self.fingerprint_id = "7144F133-D147-41EB-ADFF-67B44D61BEEF"
        self.search_id = str(uuid.uuid4())
        self.fingerprint_id = str(uuid.uuid4()).upper()

        self.jobs_per_page = 50
        self.seen_urls = set()

    def scrape(self, scraper_input: ScraperInput) -> JobResponse:
        """
        Scrapes Monster for jobs with scraper_input criteria.
        :param scraper_input: Information about job search criteria.
        :return: JobResponse containing a list of jobs.
        """
        self.scraper_input = scraper_input
        job_list: list[JobPost] = []

        max_pages = math.ceil(scraper_input.results_wanted / self.jobs_per_page)
        for page in range(1, min(11, max_pages + 1)):
            if len(job_list) >= scraper_input.results_wanted:
                break
            logger.info(f"Monster search page: {page}")
            jobs_on_page = self._find_jobs_in_page(scraper_input, page)
            if jobs_on_page:
                job_list.extend(jobs_on_page)
            else:
                break
        return JobResponse(jobs=job_list[: scraper_input.results_wanted])

    def _find_jobs_in_page(self, scraper_input: ScraperInput, page: int) -> [JobPost]:
        """
        Scrapes a page of Monster for jobs with scraper_input criteria
        :param scraper_input:
        :param page:
        :return: jobs found on page
        """
        jobs_list = []
        payload = self._add_payload(scraper_input, (page - 1) * 50)
        try:
            res = self.session.post(self.api_url, headers=self.headers, json=payload)
            if res.status_code not in range(200, 400):
                if res.status_code == 429:
                    err = "429 Response - Blocked by Monster for too many requests"
                else:
                    err = f"Monster response status code {res.status_code} with response: {res.text}"
                logger.error(err)
                return jobs_list
        except Exception as e:
            if "Proxy responded with" in str(e):
                logger.error(f"Monster: Bad proxy")
            else:
                logger.error(f"Monster: {str(e)}")
            return jobs_list

        res_data = res.json()
        raw_jobs_list = res_data.get("jobResults", [])
        with ThreadPoolExecutor(max_workers=self.jobs_per_page) as executor:
            job_results = [
                executor.submit(self._process_job, job) for job in raw_jobs_list
            ]

        job_list = list(filter(None, (result.result() for result in job_results)))
        return job_list

    def _process_job(self, job: dict) -> JobPost | None:
        """
        Processes an individual job dict from the response
        """
        job_posting = job["jobPosting"]
        title = job_posting.get("title")
        job_url = f"{self.base_url}{job['jobId']}"
        if job_url in self.seen_urls:
            return
        self.seen_urls.add(job_url)
        job_url_direct = (
            job["apply"].get("applyUrl")
            if job.get("apply")
            and "monster.com" not in job["apply"].get("applyUrl", "")
            else None
        )

        description = job_posting.get("description", "")
        description = (
            markdown_converter(description)
            if self.scraper_input.description_format == DescriptionFormat.MARKDOWN
            else description
        )
        company = job_posting.get("hiringOrganization", {}).get("name")

        location_dict = (
            job_posting["jobLocation"][0].get("address", {})
            if job_posting.get("jobLocation")
            else {}
        )
        location = Location(
            city=location_dict.get("addressLocality"),
            state=location_dict.get("addressRegion"),
            country=location_dict.get("addressCountry"),
        )
        date_posted = parse(job_posting["datePosted"]).date()

        return JobPost(
            id=job["jobId"],
            title=title,
            company_name=company,
            location=location,
            date_posted=date_posted,
            job_url=job_url,
            description=description,
            emails=extract_emails_from_text(description) if description else None,
            job_url_direct=job_url_direct,
        )

    def _add_payload(self, scraper_input, offset) -> str:
        payload = {
            "jobAdsRequest": {
                "position": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                "placement": {
                    "property": "MobileApp",
                    "view": "CARD",
                    "type": "JOB_SEARCH",
                    "location": "JobSearchPage",
                    "channel": "MOBILE",
                },
            },
            "searchId": self.search_id,
            "offset": offset,
            "pageSize": self.jobs_per_page,
            "fingerprintId": self.fingerprint_id,
            "jobQuery": {
                "query": scraper_input.search_term,
                "locations": [
                    {
                        "address": scraper_input.location,
                        "country": "US",
                        "radius": {"value": scraper_input.distance, "unit": "mi"},
                    }
                ],
            },
        }
        return json.dumps({k: v for k, v in payload.items() if v is not None})

    headers = {
        "Host": "appsapi.monster.io",
        "accept": "*/*",
        "content-type": "application/json",
        "user-agent": "Jobr/17.0.0 (com.jobrapp.ios; build:17000.14; iOS 17.5.1) Alamofire/5.8.0",
        "accept-language": "en-US;q=1.0",
    }
