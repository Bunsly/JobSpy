from __future__ import annotations

from abc import ABC, abstractmethod

from ..jobs import (
    Enum,
    BaseModel,
    JobType,
    JobResponse,
    Country,
    DescriptionFormat,
)


class Site(Enum):
    LINKEDIN = "linkedin"
    INDEED = "indeed"
    ZIP_RECRUITER = "zip_recruiter"
    GLASSDOOR = "glassdoor"


class ScraperInput(BaseModel):
    site_type: list[Site]
    search_term: str | None = None

    location: str | None = None
    country: Country | None = Country.USA
    distance: int | None = None
    is_remote: bool = False
    job_type: JobType | None = None
    easy_apply: bool | None = None
    offset: int = 0
    linkedin_fetch_description: bool = False
    linkedin_company_ids: list[int] | None = None
    description_format: DescriptionFormat | None = DescriptionFormat.MARKDOWN

    results_wanted: int = 15
    hours_old: int | None = None


class Scraper(ABC):
    def __init__(self, site: Site, proxies: list[str] | None = None):
        self.proxies = proxies
        self.site = site

    @abstractmethod
    def scrape(self, scraper_input: ScraperInput) -> JobResponse: ...
