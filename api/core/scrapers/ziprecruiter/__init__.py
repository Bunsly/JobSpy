import json
from urllib.parse import urlparse, parse_qs

import tls_client
from fastapi import HTTPException, status
from bs4 import BeautifulSoup

from api.core.scrapers import Scraper, ScraperInput, Site
from api.core.jobs import *


class ZipRecruiterScraper(Scraper):
    def __init__(self):
        site = Site(Site.ZIP_RECRUITER)
        super().__init__(site)

        self.url = "https://www.ziprecruiter.com/jobs-search"

    def scrape(self, scraper_input: ScraperInput) -> JobResponse:
        session = tls_client.Session(
            client_identifier="chrome112", random_tls_extension_order=True
        )

        current_page = 1

        params = {
            "search": scraper_input.search_term,
            "location": scraper_input.location,
            "page": min(current_page, 10),
            "radius": scraper_input.distance,
        }

        response = session.get(
            self.url, headers=ZipRecruiterScraper.headers(), params=params
        )
        if response.status_code != status.HTTP_200_OK:
            return JobResponse(
                success=False,
                error=f"Response returned {response.status_code}",
            )

        html_string = response.content
        soup = BeautifulSoup(html_string, "html.parser")

        job_posts = soup.find_all("div", {"class": "job_content"})

        job_list: list[JobPost] = []
        for job in job_posts:
            title = job.find("h2", {"class": "title"}).text
            company = job.find("a", {"class": "company_name"}).text.strip()
            description = job.find("p", {"class": "job_snippet"}).text.strip()
            job_type_element = job.find("li", {"class": "perk_item perk_type"})
            job_type = (
                job_type_element.text.strip().lower().replace("-", "_")
                if job_type_element
                else None
            )

            url = job.find("a", {"class": "job_link"})["href"]
            date_posted = ZipRecruiterScraper.get_date_posted(job)

            job_type = job_type.replace(" ", "_") if job_type else job_type
            job_post = JobPost(
                title=title,
                description=description,
                company_name=company,
                location=ZipRecruiterScraper.get_location(job),
                job_type=job_type,
                compensation=ZipRecruiterScraper.get_compensation(job),
                date_posted=date_posted,
                delivery=Delivery(method=DeliveryEnum.URL, value=url),
            )
            job_list.append(job_post)
            if len(job_list) > 20:
                break

        script_tag = soup.find("script", {"id": "js_variables"})

        data = json.loads(script_tag.string)

        job_count = data["totalJobCount"]
        job_count = job_count.replace(",", "")
        total_pages = data["maxPages"]
        job_response = JobResponse(
            success=True,
            jobs=job_list,
            job_count=job_count,
            page=params["page"],
            total_pages=total_pages,
        )
        return job_response

    @staticmethod
    def get_interval(interval_str):
        interval_alias = {"annually": CompensationInterval.YEARLY}
        interval_str = interval_str.lower()

        if interval_str in interval_alias:
            return interval_alias[interval_str]

        return CompensationInterval(interval_str)

    @staticmethod
    def get_date_posted(job: BeautifulSoup):
        button = job.find(
            "button", {"class": "action_input save_job zrs_btn_secondary_200"}
        )
        url_time = button["data-href"]
        url_components = urlparse(url_time)
        params = parse_qs(url_components.query)
        return params.get("posted_time", [None])[0]

    @staticmethod
    def get_compensation(job: BeautifulSoup):
        pay_element = job.find("li", {"class": "perk_item perk_pay"})
        if pay_element is None:
            return None
        pay = pay_element.find("div", {"class": "value"}).find("span").text.strip()

        return ZipRecruiterScraper.create_compensation_object(pay)

    @staticmethod
    def get_location(job: BeautifulSoup):
        location_string = job.find("a", {"class": "company_location"}).text.strip()
        parts = location_string.split(", ")
        city, state = parts
        return Location(
            country="US",
            city=city,
            state=state,
        )

    @staticmethod
    def create_compensation_object(pay_string: str):
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

    @staticmethod
    def headers():
        return {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36"
        }
