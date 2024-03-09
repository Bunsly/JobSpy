"""
jobspy.scrapers.linkedin
~~~~~~~~~~~~~~~~~~~

This module contains routines to scrape LinkedIn.
"""

from __future__ import annotations

import time
import random
from typing import Optional
from datetime import datetime

from threading import Lock
from bs4.element import Tag
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse

from .. import Scraper, ScraperInput, Site
from ..exceptions import LinkedInException
from ..utils import create_session
from ...jobs import (
    JobPost,
    Location,
    JobResponse,
    JobType,
    Country,
    Compensation,
    DescriptionFormat,
)
from ..utils import (
    logger,
    extract_emails_from_text,
    get_enum_from_job_type,
    currency_parser,
    markdown_converter,
)


class LinkedInScraper(Scraper):
    base_url = "https://www.linkedin.com"
    delay = 3
    band_delay = 4
    jobs_per_page = 25

    def __init__(self, proxy: Optional[str] = None):
        """
        Initializes LinkedInScraper with the LinkedIn job search url
        """
        super().__init__(Site(Site.LINKEDIN), proxy=proxy)
        self.scraper_input = None
        self.country = "worldwide"

    def scrape(self, scraper_input: ScraperInput) -> JobResponse:
        """
        Scrapes LinkedIn for jobs with scraper_input criteria
        :param scraper_input:
        :return: job_response
        """
        self.scraper_input = scraper_input
        job_list: list[JobPost] = []
        seen_urls = set()
        url_lock = Lock()
        page = scraper_input.offset // 25 + 25 if scraper_input.offset else 0
        seconds_old = (
            scraper_input.hours_old * 3600 if scraper_input.hours_old else None
        )
        continue_search = (
            lambda: len(job_list) < scraper_input.results_wanted and page < 1000
        )
        while continue_search():
            logger.info(f"LinkedIn search page: {page // 25 + 1}")
            session = create_session(is_tls=False, has_retry=True, delay=5)
            params = {
                "keywords": scraper_input.search_term,
                "location": scraper_input.location,
                "distance": scraper_input.distance,
                "f_WT": 2 if scraper_input.is_remote else None,
                "f_JT": (
                    self.job_type_code(scraper_input.job_type)
                    if scraper_input.job_type
                    else None
                ),
                "pageNum": 0,
                "start": page + scraper_input.offset,
                "f_AL": "true" if scraper_input.easy_apply else None,
                "f_C": (
                    ",".join(map(str, scraper_input.linkedin_company_ids))
                    if scraper_input.linkedin_company_ids
                    else None
                ),
            }
            if seconds_old is not None:
                params["f_TPR"] = f"r{seconds_old}"

            params = {k: v for k, v in params.items() if v is not None}
            try:
                response = session.get(
                    f"{self.base_url}/jobs-guest/jobs/api/seeMoreJobPostings/search?",
                    params=params,
                    allow_redirects=True,
                    proxies=self.proxy,
                    headers=self.headers,
                    timeout=10,
                )
                if response.status_code not in range(200, 400):
                    if response.status_code == 429:
                        err = (
                            f"429 Response - Blocked by LinkedIn for too many requests"
                        )
                    else:
                        err = f"LinkedIn response status code {response.status_code}"
                        err += f" - {response.text}"
                    logger.error(err)
                    return JobResponse(jobs=job_list)
            except Exception as e:
                if "Proxy responded with" in str(e):
                    logger.error(f"LinkedIn: Bad proxy")
                else:
                    logger.error(f"LinkedIn: {str(e)}")
                return JobResponse(jobs=job_list)

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
                    job_url = f"{self.base_url}/jobs/view/{job_id}"

                with url_lock:
                    if job_url in seen_urls:
                        continue
                    seen_urls.add(job_url)
                try:
                    fetch_desc = scraper_input.linkedin_fetch_description
                    job_post = self._process_job(job_card, job_url, fetch_desc)
                    if job_post:
                        job_list.append(job_post)
                    if not continue_search():
                        break
                except Exception as e:
                    raise LinkedInException(str(e))

            if continue_search():
                time.sleep(random.uniform(self.delay, self.delay + self.band_delay))
                page += self.jobs_per_page

        job_list = job_list[: scraper_input.results_wanted]
        return JobResponse(jobs=job_list)

    def _process_job(
        self, job_card: Tag, job_url: str, full_descr: bool
    ) -> Optional[JobPost]:
        salary_tag = job_card.find("span", class_="job-search-card__salary-info")

        compensation = None
        if salary_tag:
            salary_text = salary_tag.get_text(separator=" ").strip()
            salary_values = [currency_parser(value) for value in salary_text.split("-")]
            salary_min = salary_values[0]
            salary_max = salary_values[1]
            currency = salary_text[0] if salary_text[0] != "$" else "USD"

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
        location = self._get_location(metadata_card)

        datetime_tag = (
            metadata_card.find("time", class_="job-search-card__listdate")
            if metadata_card
            else None
        )
        date_posted = description = job_type = None
        if datetime_tag and "datetime" in datetime_tag.attrs:
            datetime_str = datetime_tag["datetime"]
            try:
                date_posted = datetime.strptime(datetime_str, "%Y-%m-%d")
            except:
                date_posted = None
        benefits_tag = job_card.find("span", class_="result-benefits__text")
        if full_descr:
            description, job_type = self._get_job_description(job_url)

        return JobPost(
            title=title,
            company_name=company,
            company_url=company_url,
            location=location,
            date_posted=date_posted,
            job_url=job_url,
            compensation=compensation,
            job_type=job_type,
            description=description,
            emails=extract_emails_from_text(description) if description else None,
        )

    def _get_job_description(
        self, job_page_url: str
    ) -> tuple[None, None] | tuple[str | None, tuple[str | None, JobType | None]]:
        """
        Retrieves job description by going to the job page url
        :param job_page_url:
        :return: description or None
        """
        try:
            session = create_session(is_tls=False, has_retry=True)
            response = session.get(
                job_page_url, headers=self.headers, timeout=5, proxies=self.proxy
            )
            response.raise_for_status()
        except:
            return None, None
        if response.url == "https://www.linkedin.com/signup":
            return None, None

        soup = BeautifulSoup(response.text, "html.parser")
        div_content = soup.find(
            "div", class_=lambda x: x and "show-more-less-html__markup" in x
        )
        description = None
        if div_content is not None:

            def remove_attributes(tag):
                for attr in list(tag.attrs):
                    del tag[attr]
                return tag

            div_content = remove_attributes(div_content)
            description = div_content.prettify(formatter="html")
            if self.scraper_input.description_format == DescriptionFormat.MARKDOWN:
                description = markdown_converter(description)
        return description, self._parse_job_type(soup)

    def _get_location(self, metadata_card: Optional[Tag]) -> Location:
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
                country = Country.from_string(country)
                location = Location(city=city, state=state, country=country)
        return location

    @staticmethod
    def _parse_job_type(soup_job_type: BeautifulSoup) -> list[JobType] | None:
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

    @staticmethod
    def job_type_code(job_type_enum: JobType) -> str:
        return {
            JobType.FULL_TIME: "F",
            JobType.PART_TIME: "P",
            JobType.INTERNSHIP: "I",
            JobType.CONTRACT: "C",
            JobType.TEMPORARY: "T",
        }.get(job_type_enum, "")

    headers = {
        "authority": "www.linkedin.com",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "max-age=0",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
