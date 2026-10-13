from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import date
from enum import Enum

from pydantic import BaseModel, Field, FilePath, field_validator, model_validator


class JobType(Enum):
    FULL_TIME = "fulltime"
    PART_TIME = "parttime"
    CONTRACT = "contract"
    TEMPORARY = "temporary"
    INTERNSHIP = "internship"
    PER_DIEM = "perdiem"
    OTHER = "other"
    VOLUNTEER = "volunteer"


class Country(Enum):
    ARGENTINA = "argentina"
    AUSTRALIA = "australia"
    AUSTRIA = "austria"
    BAHRAIN = "bahrain"
    BELGIUM = "belgium"
    BRAZIL = "brazil"
    CANADA = "canada"
    CHILE = "chile"
    CHINA = "china"
    COLOMBIA = "colombia"
    COSTARICA = "costa rica"
    CZECHREPUBLIC = "czech republic"
    DENMARK = "denmark"
    ECUADOR = "ecuador"
    EGYPT = "egypt"
    FINLAND = "finland"
    FRANCE = "france"
    GERMANY = "germany"
    GREECE = "greece"
    HONGKONG = "hong kong"
    HUNGARY = "hungary"
    INDIA = "india"
    INDONESIA = "indonesia"
    IRELAND = "ireland"
    ISRAEL = "israel"
    ITALY = "italy"
    JAPAN = "japan"
    KUWAIT = "kuwait"
    LUXEMBOURG = "luxembourg"
    MALAYSIA = "malaysia"
    MEXICO = "mexico"
    MOROCCO = "morocco"
    NETHERLANDS = "netherlands"
    NEWZEALAND = "new zealand"
    NIGERIA = "nigeria"
    NORWAY = "norway"
    OMAN = "oman"
    PAKISTAN = "pakistan"
    PANAMA = "panama"
    PERU = "peru"
    PHILIPPINES = "philippines"
    POLAND = "poland"
    PORTUGAL = "portugal"
    QATAR = "qatar"
    ROMANIA = "romania"
    SAUDIARABIA = "saudi arabia"
    SINGAPORE = "singapore"
    SOUTHAFRICA = "south africa"
    SOUTHKOREA = "south korea"
    SPAIN = "spain"
    SWEDEN = "sweden"
    SWITZERLAND = "switzerland"
    TAIWAN = "taiwan"
    THAILAND = "thailand"
    TURKEY = "türkiye"
    UKRAINE = "ukraine"
    UNITEDARABEMIRATES = "united arab emirates"
    UK = "uk"
    USA = "usa"
    URUGUAY = "uruguay"
    VENEZUELA = "venezuela"
    VIETNAM = "vietnam"

    @classmethod
    def _missing_(cls, value: object) -> Country | None:
        name = str(value).strip().lower()
        name = country_aliases.get(name, name)
        return next((country for country in cls if country.value == name), None)


country_aliases = {
    "czechia": "czech republic",
    "turkey": "türkiye",
    "uae": "united arab emirates",
    "united kingdom": "uk",
    "us": "usa",
    "united states": "usa",
}


class Location(BaseModel):
    country: Country | str | None = None
    city: str | None = None
    state: str | None = None

    def display_location(self) -> str:
        parts = [self.city, self.state]
        country = self.country
        if isinstance(country, str):
            text = country
            try:
                country = Country(text)
            except ValueError:
                parts.append(text)
        if isinstance(country, Country):
            name = country.value
            parts.append(name.upper() if name in ("usa", "uk") else name.title())
        return ", ".join(part for part in parts if part and part.strip())


class CompensationInterval(Enum):
    YEARLY = "yearly"
    MONTHLY = "monthly"
    WEEKLY = "weekly"
    DAILY = "daily"
    HOURLY = "hourly"


class Compensation(BaseModel):
    interval: CompensationInterval | None = None
    min_amount: float | None = None
    max_amount: float | None = None
    currency: str | None = None


class DescriptionFormat(Enum):
    MARKDOWN = "markdown"
    HTML = "html"
    PLAIN = "plain"


class JobPost(BaseModel):
    id: str | None = None
    title: str
    company_name: str | None
    job_url: str
    job_url_direct: str | None = None
    location: Location | None

    description: str | None = None
    company_url: str | None = None
    company_url_direct: str | None = None

    job_type: list[JobType] | None = None
    compensation: Compensation | None = None
    date_posted: date | None = None
    emails: list[str] | None = None
    is_remote: bool | None = None
    listing_type: str | None = None

    job_level: str | None = None
    company_industry: str | None = None
    company_addresses: str | None = None
    company_num_employees: str | None = None
    company_revenue: str | None = None
    company_description: str | None = None
    company_logo: str | None = None
    job_function: str | None = None
    skills: list[str] | None = None
    experience_range: str | None = None
    company_rating: float | None = None
    company_reviews_count: int | None = None
    vacancy_count: int | None = None
    work_from_home_type: str | None = None  # Naukri: "Hybrid", "Remote", ...


class Site(Enum):
    LINKEDIN = "linkedin"
    INDEED = "indeed"
    ZIP_RECRUITER = "zip_recruiter"
    GLASSDOOR = "glassdoor"
    GOOGLE = "google"
    BAYT = "bayt"
    NAUKRI = "naukri"
    BDJOBS = "bdjobs"
    HELLOWORK = "hellowork"


class ScraperInput(BaseModel):
    site_name: list[Site] = Field(
        [site for site in Site if site != Site.GOOGLE], min_length=1
    )
    search_term: str | None = None
    google_search_term: str | None = None

    location: str | None = None
    country_indeed: Country = Country.USA
    distance: int | None = Field(None, ge=0)
    is_remote: bool = False
    job_type: JobType | None = None
    easy_apply: bool | None = None
    offset: int = Field(0, ge=0)
    fetch_description: bool = False
    linkedin_fetch_description: bool = False
    """Deprecated since 1.2.0: use fetch_description; will be removed in 2.0."""
    linkedin_company_ids: list[int] | None = None
    description_format: DescriptionFormat = DescriptionFormat.MARKDOWN

    results_wanted: int = Field(15, ge=0)
    hours_old: int | None = Field(None, ge=0)
    enforce_annual_salary: bool = False
    proxies: list[str] = []
    ca_cert: FilePath | None = None
    user_agent: str | None = None
    verbose: int = Field(1, ge=0, le=2)

    @field_validator("site_name", "proxies", mode="before")
    @classmethod
    def _one_or_several(cls, value: object) -> object:
        return [value] if isinstance(value, (str, Enum)) else value

    @model_validator(mode="after")
    def _merge_linkedin_fetch_description(self) -> ScraperInput:
        if self.linkedin_fetch_description:
            self.fetch_description = True
        return self


class Scraper(ABC):
    def __init__(self) -> None:
        self.log = logging.getLogger(type(self).__module__)

    @abstractmethod
    def scrape(self, scraper_input: ScraperInput) -> list[JobPost]: ...
