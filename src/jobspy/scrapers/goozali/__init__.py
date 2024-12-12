"""
jobspy.scrapers.Goozali
~~~~~~~~~~~~~~~~~~~

This module contains routines to scrape Goozali.
"""

from __future__ import annotations

import math
import time
import random
import regex as re
from typing import Optional
from datetime import datetime

from bs4.element import Tag
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse, unquote
from requests.exceptions import RetryError, RequestException
from urllib3.exceptions import MaxRetryError
from .constants import headers
from .. import Scraper, ScraperInput, Site
from ..exceptions import GoozaliException
from ..utils import create_session, remove_attributes, create_logger
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
    extract_emails_from_text,
    get_enum_from_job_type,
    currency_parser,
    markdown_converter,
)

logger = create_logger("Goozali")


class GoozaliScraper(Scraper):
    base_url = "https://www.Goozali.com"
    delay = 3
    band_delay = 4
    jobs_per_page = 25

    def __init__(
        self, proxies: list[str] | str | None = None, ca_cert: str | None = None
    ):
        """
        Initializes GoozaliScraper with the Goozalijob search url
        """
        super().__init__(Site.GOOZALI, proxies=proxies, ca_cert=ca_cert)
        self.session = create_session(
            proxies=self.proxies,
            ca_cert=ca_cert,
            is_tls=False,
            has_retry=True,
            delay=5,
            clear_cookies=True,
        )
        self.session.headers.update(headers)
        self.scraper_input = None
        self.country = "worldwide"
        self.job_url_direct_regex = re.compile(r'(?<=\?url=)[^"]+')

    def scrape(self, scraper_input: ScraperInput) -> JobResponse:
        """
        Scrapes Goozali for jobs with scraper_input criteria
        :param scraper_input:
        :return: job_response
        """
        self.scraper_input = scraper_input
        job_list: list[JobPost] = []
        seen_ids = set()
        # create url
        # create session -> run the api
        # model the response with models
        # create map columnId to Column object
        # filter result by Field like the web
        # filter by date
        # map to JobResponse Object
        return JobResponse(jobs=job_list)

    def _get_job_details(self, job_id: str) -> dict:
        """
        Retrieves job description and other job details by going to the job page url
        :param job_page_url:
        :return: dict
        """
        try:
            response = self.session.get(
                f"{self.base_url}/jobs/view/{job_id}", timeout=5
            )
            response.raise_for_status()
        except:
            return {}
        if "Goozali.com/signup" in response.url:
            return {}

        soup = BeautifulSoup(response.text, "html.parser")
        div_content = soup.find(
            "div", class_=lambda x: x and "show-more-less-html__markup" in x
        )
        description = None
        if div_content is not None:
            div_content = remove_attributes(div_content)
            description = div_content.prettify(formatter="html")
            if self.scraper_input.description_format == DescriptionFormat.MARKDOWN:
                description = markdown_converter(description)

        h3_tag = soup.find(
            "h3", text=lambda text: text and "Job function" in text.strip()
        )

        job_function = None
        if h3_tag:
            job_function_span = h3_tag.find_next(
                "span", class_="description__job-criteria-text"
            )
            if job_function_span:
                job_function = job_function_span.text.strip()

        company_logo = (
            logo_image.get("data-delayed-url")
            if (logo_image := soup.find("img", {"class": "artdeco-entity-image"}))
            else None
        )
        return {
            "description": description,
            "job_level": self._parse_job_level(soup),
            "company_industry": self._parse_company_industry(soup),
            "job_type": self._parse_job_type(soup),
            "job_url_direct": self._parse_job_url_direct(soup),
            "company_logo": company_logo,
            "job_function": job_function,
        }

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
    def _parse_job_level(soup_job_level: BeautifulSoup) -> str | None:
        """
        Gets the job level from job page
        :param soup_job_level:
        :return: str
        """
        h3_tag = soup_job_level.find(
            "h3",
            class_="description__job-criteria-subheader",
            string=lambda text: "Seniority level" in text,
        )
        job_level = None
        if h3_tag:
            job_level_span = h3_tag.find_next_sibling(
                "span",
                class_="description__job-criteria-text description__job-criteria-text--criteria",
            )
            if job_level_span:
                job_level = job_level_span.get_text(strip=True)

        return job_level

    @staticmethod
    def _parse_company_industry(soup_industry: BeautifulSoup) -> str | None:
        """
        Gets the company industry from job page
        :param soup_industry:
        :return: str
        """
        h3_tag = soup_industry.find(
            "h3",
            class_="description__job-criteria-subheader",
            string=lambda text: "Industries" in text,
        )
        industry = None
        if h3_tag:
            industry_span = h3_tag.find_next_sibling(
                "span",
                class_="description__job-criteria-text description__job-criteria-text--criteria",
            )
            if industry_span:
                industry = industry_span.get_text(strip=True)

        return industry

    def _parse_job_url_direct(self, soup: BeautifulSoup) -> str | None:
        """
        Gets the job url direct from job page
        :param soup:
        :return: str
        """
        job_url_direct = None
        job_url_direct_content = soup.find("code", id="applyUrl")
        if job_url_direct_content:
            job_url_direct_match = self.job_url_direct_regex.search(
                job_url_direct_content.decode_contents().strip()
            )
            if job_url_direct_match:
                job_url_direct = unquote(job_url_direct_match.group())

        return job_url_direct

    @staticmethod
    def job_type_code(job_type_enum: JobType) -> str:
        return {
            JobType.FULL_TIME: "F",
            JobType.PART_TIME: "P",
            JobType.INTERNSHIP: "I",
            JobType.CONTRACT: "C",
            JobType.TEMPORARY: "T",
        }.get(job_type_enum, "")
