import json
from typing import Optional
from urllib.parse import urlparse, parse_qs

import tls_client
from fastapi import status
from bs4 import BeautifulSoup

from api.core.scrapers import Scraper, ScraperInput, Site
from api.core.jobs import *


class ZipRecruiterScraper(Scraper):
    def __init__(self):
        """
        Initializes LinkedInScraper with the ZipRecruiter job search url
        """
        site = Site(Site.ZIP_RECRUITER)
        super().__init__(site)

        self.url = "https://www.ziprecruiter.com/jobs-search"

    def scrape(self, scraper_input: ScraperInput) -> JobResponse:
        """
        Scrapes ZipRecruiter for jobs with scraper_input criteria
        :param scraper_input:
        :return: job_response
        """
        session = tls_client.Session(
            client_identifier="chrome112", random_tls_extension_order=True
        )

        job_list: list[JobPost] = []
        page = 1
        processed_jobs, job_count = 0, 0
        seen_urls = set()
        while len(job_list) < scraper_input.results_wanted:
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
                self.url, headers=ZipRecruiterScraper.headers(), params=params
            )
            print(response.url)
            if response.status_code != status.HTTP_200_OK:
                return JobResponse(
                    success=False,
                    error=f"Response returned {response.status_code}",
                )

            html_string = response.content
            soup = BeautifulSoup(html_string, "html.parser")
            if page == 1:
                script_tag = soup.find("script", {"id": "js_variables"})
                data = json.loads(script_tag.string)

                job_count = data["totalJobCount"]
                job_count = int(job_count.replace(",", ""))

            job_posts = soup.find_all("div", {"class": "job_content"})

            for job in job_posts:
                processed_jobs += 1
                job_url = job.find("a", {"class": "job_link"})["href"]
                if job_url in seen_urls:
                    continue
                title = job.find("h2", {"class": "title"}).text
                company = job.find("a", {"class": "company_name"}).text.strip()
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
                job_list.append(job_post)
                if (
                    len(job_list) >= scraper_input.results_wanted
                    or processed_jobs >= job_count
                ):
                    break

            if (
                len(job_list) >= scraper_input.results_wanted
                or processed_jobs >= job_count
            ):
                break

            page += 1

        job_list = job_list[: scraper_input.results_wanted]
        job_response = JobResponse(
            success=True,
            jobs=job_list,
            job_count=job_count,
        )
        return job_response

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
            country="US",
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
