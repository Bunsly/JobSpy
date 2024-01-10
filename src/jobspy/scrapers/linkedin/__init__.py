"""
jobspy.scrapers.linkedin
~~~~~~~~~~~~~~~~~~~

This module contains routines to scrape LinkedIn.
"""
import random
from typing import Optional
from datetime import datetime

import requests
import time
from requests.exceptions import ProxyError
from bs4 import BeautifulSoup
from bs4.element import Tag
from threading import Lock
from urllib.parse import urlparse, urlunparse

from .. import Scraper, ScraperInput, Site
from ..exceptions import LinkedInException
from ..utils import create_session
from ...jobs import JobPost, Location, JobResponse, JobType, Country, Compensation
from ..utils import count_urgent_words, extract_emails_from_text, get_enum_from_job_type, currency_parser


class LinkedInScraper(Scraper):
    DELAY = 3

    def __init__(self, proxy: Optional[str] = None):
        """
        Initializes LinkedInScraper with the LinkedIn job search url
        """
        site = Site(Site.LINKEDIN)
        self.country = "worldwide"
        self.url = "https://www.linkedin.com"
        super().__init__(site, proxy=proxy)

    def scrape(self, scraper_input: ScraperInput) -> JobResponse:
        """
        Scrapes LinkedIn for jobs with scraper_input criteria
        :param scraper_input:
        :return: job_response
        """
        job_list: list[JobPost] = []
        seen_urls = set()
        url_lock = Lock()
        page = scraper_input.offset // 25 + 25 if scraper_input.offset else 0

        def job_type_code(job_type_enum):
            mapping = {
                JobType.FULL_TIME: "F",
                JobType.PART_TIME: "P",
                JobType.INTERNSHIP: "I",
                JobType.CONTRACT: "C",
                JobType.TEMPORARY: "T",
            }

            return mapping.get(job_type_enum, "")

        while len(job_list) < scraper_input.results_wanted and page < 1000:
            session = create_session(is_tls=False, has_retry=True, delay=5)
            params = {
                "keywords": scraper_input.search_term,
                "location": scraper_input.location,
                "distance": scraper_input.distance,
                "f_WT": 2 if scraper_input.is_remote else None,
                "f_JT": job_type_code(scraper_input.job_type)
                if scraper_input.job_type
                else None,
                "pageNum": 0,
                "start": page + scraper_input.offset,
                "f_AL": "true" if scraper_input.easy_apply else None,
            }

            params = {k: v for k, v in params.items() if v is not None}
            try:
                response = session.get(
                    f"{self.url}/jobs-guest/jobs/api/seeMoreJobPostings/search?",
                    params=params,
                    allow_redirects=True,
                    proxies=self.proxy,
                    headers=self.headers(),
                    timeout=10,
                )
                response.raise_for_status()

            except requests.HTTPError as e:
                raise LinkedInException(f"bad response status code: {e.response.status_code}")
            except ProxyError as e:
                raise LinkedInException("bad proxy")
            except Exception as e:
                raise LinkedInException(str(e))

            soup = BeautifulSoup(response.text, "html.parser")
            job_cards = soup.find_all("div", class_="base-search-card")
            if len(job_cards) == 0:
                return JobResponse(jobs=job_list)

            for job_card in job_cards:
                job_url = None
                href_tag = job_card.find("a", class_="base-card__full-link")
                if href_tag and "href" in href_tag.attrs:
                    href = href_tag.attrs["href"].split("?")[0]
                    job_id = href.split("-")[-1]
                    job_url = f"{self.url}/jobs/view/{job_id}"

                with url_lock:
                    if job_url in seen_urls:
                        continue
                    seen_urls.add(job_url)

                # Call process_job directly without threading
                try:
                    job_post = self.process_job(job_card, job_url)
                    if job_post:
                        job_list.append(job_post)
                except Exception as e:
                    raise LinkedInException("Exception occurred while processing jobs")

            page += 25
            time.sleep(random.uniform(LinkedInScraper.DELAY, LinkedInScraper.DELAY + 2))

        job_list = job_list[: scraper_input.results_wanted]
        return JobResponse(jobs=job_list)

    def process_job(self, job_card: Tag, job_url: str) -> Optional[JobPost]:
        salary_tag = job_card.find('span', class_='job-search-card__salary-info')

        compensation = None
        if salary_tag:
            salary_text = salary_tag.get_text(separator=' ').strip()
            salary_values = [currency_parser(value) for value in salary_text.split('-')]
            salary_min = salary_values[0]
            salary_max = salary_values[1]
            currency = salary_text[0] if salary_text[0] != '$' else 'USD'

            compensation = Compensation(
                min_amount=int(salary_min),
                max_amount=int(salary_max),
                currency=currency,
            )

        title_tag = job_card.find("span", class_="sr-only")
        title = title_tag.get_text(strip=True) if title_tag else "N/A"

        company_tag = job_card.find("h4", class_="base-search-card__subtitle")
        company_a_tag = company_tag.find("a") if company_tag else None
        company_url = (
            urlunparse(urlparse(company_a_tag.get("href"))._replace(query=""))
            if company_a_tag and company_a_tag.has_attr("href")
            else ""
        )
        company = company_a_tag.get_text(strip=True) if company_a_tag else "N/A"

        metadata_card = job_card.find("div", class_="base-search-card__metadata")
        location = self.get_location(metadata_card)

        datetime_tag = (
            metadata_card.find("time", class_="job-search-card__listdate")
            if metadata_card
            else None
        )
        date_posted = None
        if datetime_tag and "datetime" in datetime_tag.attrs:
            datetime_str = datetime_tag["datetime"]
            try:
                date_posted = datetime.strptime(datetime_str, "%Y-%m-%d")
            except Exception as e:
                date_posted = None
        benefits_tag = job_card.find("span", class_="result-benefits__text")
        benefits = " ".join(benefits_tag.get_text().split()) if benefits_tag else None

        # removed to speed up scraping
        # description, job_type = self.get_job_description(job_url)

        return JobPost(
            title=title,
            company_name=company,
            company_url=company_url,
            location=location,
            date_posted=date_posted,
            job_url=job_url,
            compensation=compensation,
            benefits=benefits,
            # job_type=job_type,
            # description=description,
            # emails=extract_emails_from_text(description) if description else None,
            # num_urgent_words=count_urgent_words(description) if description else None,
        )

    def get_job_description(
        self, job_page_url: str
    ) -> tuple[None, None] | tuple[str | None, tuple[str | None, JobType | None]]:
        """
        Retrieves job description by going to the job page url
        :param job_page_url:
        :return: description or None
        """
        try:
            session = create_session(is_tls=False, has_retry=True)
            response = session.get(job_page_url, timeout=5, proxies=self.proxy)
            response.raise_for_status()
        except requests.HTTPError as e:
            return None, None
        except Exception as e:
            return None, None
        if response.url == "https://www.linkedin.com/signup":
            return None, None

        soup = BeautifulSoup(response.text, "html.parser")
        div_content = soup.find(
            "div", class_=lambda x: x and "show-more-less-html__markup" in x
        )

        description = None
        if div_content:
            description = " ".join(div_content.get_text().split()).strip()

        def get_job_type(
            soup_job_type: BeautifulSoup,
        ) -> list[JobType] | None:
            """
            Gets the job type from job page
            :param soup_job_type:
            :return: JobType
            """
            h3_tag = soup_job_type.find(
                "h3",
                class_="description__job-criteria-subheader",
                string=lambda text: "Employment type" in text,
            )

            employment_type = None
            if h3_tag:
                employment_type_span = h3_tag.find_next_sibling(
                    "span",
                    class_="description__job-criteria-text description__job-criteria-text--criteria",
                )
                if employment_type_span:
                    employment_type = employment_type_span.get_text(strip=True)
                    employment_type = employment_type.lower()
                    employment_type = employment_type.replace("-", "")

            return [get_enum_from_job_type(employment_type)] if employment_type else []

        return description, get_job_type(soup)

    def get_location(self, metadata_card: Optional[Tag]) -> Location:
        """
        Extracts the location data from the job metadata card.
        :param metadata_card
        :return: location
        """
        location = Location(country=Country.from_string(self.country))
        if metadata_card is not None:
            location_tag = metadata_card.find(
                "span", class_="job-search-card__location"
            )
            location_string = location_tag.text.strip() if location_tag else "N/A"
            parts = location_string.split(", ")
            if len(parts) == 2:
                city, state = parts
                location = Location(
                    city=city,
                    state=state,
                    country=Country.from_string(self.country),
                )
            elif len(parts) == 3:
                city, state, country = parts
                location = Location(
                    city=city,
                    state=state,
                    country=Country.from_string(country),
                )

        return location

    @staticmethod
    def headers() -> dict:
        return {
            'authority': 'www.linkedin.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            # 'sec-ch-ua-mobile': '?0',
            # 'sec-ch-ua-platform': '"macOS"',
            # 'sec-fetch-dest': 'document',
            # 'sec-fetch-mode': 'navigate',
            # 'sec-fetch-site': 'none',
            # 'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
