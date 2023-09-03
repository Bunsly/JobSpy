from typing import Optional, Tuple
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from .. import Scraper, ScraperInput, Site
from ...jobs import JobPost, Location, JobResponse, JobType, Compensation, CompensationInterval


class LinkedInScraper(Scraper):
    def __init__(self):
        """
        Initializes LinkedInScraper with the LinkedIn job search url
        """
        site = Site(Site.LINKEDIN)
        url = "https://www.linkedin.com"
        super().__init__(site, url)

    def scrape(self, scraper_input: ScraperInput) -> JobResponse:
        """
        Scrapes LinkedIn for jobs with scraper_input criteria
        :param scraper_input:
        :return: job_response
        """
        job_list: list[JobPost] = []
        seen_urls = set()
        page, processed_jobs, job_count = 0, 0, 0

        def job_type_code(job_type):
            mapping = {
                JobType.FULL_TIME: "F",
                JobType.PART_TIME: "P",
                JobType.INTERNSHIP: "I",
                JobType.CONTRACT: "C",
                JobType.TEMPORARY: "T",
            }

            return mapping.get(job_type, "")

        with requests.Session() as session:
            while len(job_list) < scraper_input.results_wanted:
                params = {
                    "keywords": scraper_input.search_term,
                    "location": scraper_input.location,
                    "distance": scraper_input.distance,
                    "f_WT": 2 if scraper_input.is_remote else None,
                    "f_JT": job_type_code(scraper_input.job_type)
                    if scraper_input.job_type
                    else None,
                    "pageNum": page,
                    "f_AL": "true" if scraper_input.easy_apply else None,
                }

                params = {k: v for k, v in params.items() if v is not None}
                response = session.get(
                    f"{self.url}/jobs/search", params=params, allow_redirects=True
                )

                if response.status_code != 200:
                    return JobResponse(
                        success=False,
                        error=f"Response returned {response.status_code}",
                    )

                soup = BeautifulSoup(response.text, "html.parser")

                if page == 0:
                    job_count_text = soup.find(
                        "span", class_="results-context-header__job-count"
                    ).text
                    job_count = int("".join(filter(str.isdigit, job_count_text)))

                for job_card in soup.find_all(
                    "div",
                    class_="base-card relative w-full hover:no-underline focus:no-underline base-card--link base-search-card base-search-card--link job-search-card",
                ):
                    processed_jobs += 1
                    data_entity_urn = job_card.get("data-entity-urn", "")
                    job_id = (
                        data_entity_urn.split(":")[-1] if data_entity_urn else "N/A"
                    )
                    job_url = f"{self.url}/jobs/view/{job_id}"
                    if job_url in seen_urls:
                        continue
                    seen_urls.add(job_url)
                    job_info = job_card.find("div", class_="base-search-card__info")
                    if job_info is None:
                        continue
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
                    description, job_type = LinkedInScraper.get_description(job_url)
                    if datetime_tag:
                        datetime_str = datetime_tag["datetime"]
                        date_posted = datetime.strptime(datetime_str, "%Y-%m-%d")
                    else:
                        date_posted = None

                    job_post = JobPost(
                        title=title,
                        description=description,
                        company_name=company,
                        location=location,
                        date_posted=date_posted,
                        job_url=job_url,
                        job_type=job_type,
                        compensation=Compensation(interval=CompensationInterval.YEARLY, currency="USD")
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
            total_results=job_count,
        )
        return job_response

    @staticmethod
    def get_description(job_page_url: str) -> Optional[str]:
        """
        Retrieves job description by going to the job page url
        :param job_page_url:
        :return: description or None
        """
        response = requests.get(job_page_url, allow_redirects=True)
        if response.status_code not in range(200, 400):
            return None, None

        soup = BeautifulSoup(response.text, "html.parser")
        div_content = soup.find(
            "div", class_=lambda x: x and "show-more-less-html__markup" in x
        )

        text_content = None
        if div_content:
            text_content = " ".join(div_content.get_text().split()).strip()

        def get_job_type(
            soup: BeautifulSoup,
        ) -> Tuple[Optional[str], Optional[JobType]]:
            """
            Gets the job type from job page
            :param soup:
            :return: JobType
            """
            h3_tag = soup.find(
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

            return JobType(employment_type)

        return text_content, get_job_type(soup)

    @staticmethod
    def get_location(metadata_card: Optional[Tag]) -> Location:
        """
        Extracts the location data from the job metadata card.
        :param metadata_card
        :return: location
        """
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
                )

        return location
