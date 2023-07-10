import re
import json
from math import ceil

import tls_client
from bs4 import BeautifulSoup
from fastapi import HTTPException, status

from api.core.jobs import *
from api.core.scrapers import Scraper, ScraperInput, Site


class ParsingException(Exception):
    pass


class IndeedScraper(Scraper):
    def __init__(self):
        site = Site(Site.INDEED)
        super().__init__(site)
        self.url = "https://www.indeed.com/jobs"

    def scrape(self, scraper_input: ScraperInput) -> JobResponse:
        session = tls_client.Session(
            client_identifier="chrome112", random_tls_extension_order=True
        )

        params = {
            "q": scraper_input.search_term,
            "l": scraper_input.location,
            "filter": 0,
            "start": 0,
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
        total_pages = ceil(total_num_jobs / 15)

        job_list: list[JobPost] = []
        if not jobs.get('metaData', {}).get("mosaicProviderJobCardsModel", {}).get("results"):
            return JobResponse(
                success=False,
                error="No jobs found",
            )

        page_number = jobs["metaData"]["mosaicProviderJobCardsModel"]["pageNumber"]
        for job in jobs["metaData"]["mosaicProviderJobCardsModel"]["results"]:
            snippet_html = BeautifulSoup(job["snippet"], "html.parser")

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
                        min_amount=extracted_salary.get("max"),
                        max_amount=extracted_salary.get("min"),
                        currency=currency,
                    )

            job_type = IndeedScraper.get_job_type(job)
            if job.get("thirdPartyApplyUrl"):
                delivery = Delivery(
                    method=DeliveryEnum.URL, value=job["thirdPartyApplyUrl"]
                )
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

        job_response = JobResponse(
            success=True,
            jobs=job_list,
            job_count=total_num_jobs,
            page=page_number,
            total_pages=total_pages,
        )
        return job_response

    @staticmethod
    def get_job_type(data):
        for taxonomy in data["taxonomyAttributes"]:
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

        script_tag = IndeedScraper.find_mosaic_script(soup)

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
            raise ParsingException("Could not find a script tag containing mosaic provider data")

    @staticmethod
    def total_jobs(soup):
        script = soup.find("script", string=lambda t: "window._initialData" in t)

        pattern = re.compile(r"window._initialData\s*=\s*({.*})\s*;", re.DOTALL)
        match = pattern.search(script.string)
        total_num_jobs = 0
        if match:
            json_str = match.group(1)
            data = json.loads(json_str)
            total_num_jobs = data["searchTitleBarModel"]["totalNumResults"]
        return total_num_jobs

    @staticmethod
    def find_mosaic_script(soup):
        script_tags = soup.find_all("script")
        for script_tag in script_tags:
            if (
                script_tag.string
                and "mosaic.providerData" in script_tag.string
                and "mosaic-provider-jobcards" in script_tag.string
            ):
                return script_tag
        return None
