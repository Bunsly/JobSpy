from math import ceil

import requests
from bs4 import BeautifulSoup

from api.core.scrapers import Scraper, ScraperInput, Site
from api.core.jobs import *
from api.core.utils import handle_response


class LinkedInScraper(Scraper):
    def __init__(self):
        site = Site(Site.LINKEDIN)
        super().__init__(site)

        self.url = "https://www.linkedin.com/jobs"

    def scrape(self, scraper_input: ScraperInput) -> JobResponse:
        params = {"pageNum": scraper_input.page - 1, "location": scraper_input.location}

        self.url = f"{self.url}/{scraper_input.search_term}-jobs"
        response = requests.get(self.url, params=params)
        success, result = handle_response(response)
        if not success:
            return result

        soup = BeautifulSoup(response.text, "html.parser")

        job_list: list[JobPost] = []
        for job_card in soup.find_all(
            "div",
            class_="base-card relative w-full hover:no-underline focus:no-underline base-card--link base-search-card base-search-card--link job-search-card",
        ):
            job_url_tag = job_card.find("a", class_="base-card__full-link")
            job_url = job_url_tag["href"] if job_url_tag else "N/A"

            job_info = job_card.find("div", class_="base-search-card__info")
            if job_info is not None:
                title_tag = job_info.find("h3", class_="base-search-card__title")
                title = title_tag.text.strip() if title_tag else "N/A"

                company_tag = job_info.find("a", class_="hidden-nested-link")
                company = company_tag.text.strip() if company_tag else "N/A"

                metadata_card = job_info.find(
                    "div", class_="base-search-card__metadata"
                )
                location: Location = LinkedInScraper.get_location(metadata_card)

                datetime_tag = metadata_card.find(
                    "time", class_="job-search-card__listdate"
                )
                if datetime_tag:
                    datetime_str = datetime_tag["datetime"]
                    date_posted = datetime.strptime(datetime_str, "%Y-%m-%d")

            job_post = JobPost(
                title=title,
                company_name=company,
                location=location,
                date_posted=date_posted,
                delivery=Delivery(method=DeliveryEnum.URL, value=job_url),
            )
            job_list.append(job_post)

        job_count_text = soup.find(
            "span", class_="results-context-header__job-count"
        ).text
        job_count = int("".join(filter(str.isdigit, job_count_text)))
        total_pages = ceil(job_count / 25)
        job_response = JobResponse(
            jobs=job_list,
            job_count=job_count,
            page=scraper_input.page,
            total_pages=total_pages,
        )
        return job_response

    @staticmethod
    def get_location(metadata_card):
        if metadata_card is not None:
            location_tag = metadata_card.find(
                "span", class_="job-search-card__location"
            )
            location_string = location_tag.text.strip() if location_tag else "N/A"
            parts = location_string.split(", ")
            if len(parts) == 2:
                city, state = parts
                location = Location(
                    country="US",
                    city=city,
                    state=state,
                )

        return location
