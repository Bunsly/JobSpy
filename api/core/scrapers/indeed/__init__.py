import json
import re
import math

import tls_client
from bs4 import BeautifulSoup

from .. import Scraper, ScraperInput, Site
from ...jobs import *


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
            "start": 0 if scraper_input.page is None else (scraper_input.page - 1) * 10,
        }

        response = session.get(self.url, params=params)
        if response.status_code != 200:
            return {"message": f"Error - Status Code: {response.status_code}"}

        soup = BeautifulSoup(response.content, "html.parser")

        jobs = IndeedScraper.parse_jobs(soup)
        total_num_jobs = IndeedScraper.total_jobs(soup)
        total_pages = math.ceil(total_num_jobs / 15)

        job_list: list[JobPost] = []
        # page_number = jobs["metaData"]["mosaicProviderJobCardsModel"]["pageNumber"]
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
                industry=None,
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
            jobs=job_list,
            job_count=total_num_jobs,
            page=scraper_input.page,
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
    def parse_jobs(soup):
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
                return {"message": f"Could not find mosaic provider job cards data"}
        else:
            return {
                "message": f"Could not find a script tag containing mosaic provider data"
            }

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
