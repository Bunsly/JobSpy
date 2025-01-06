from pydantic import BaseModel

from jobs import Country, JobType, DescriptionFormat
from model.User import User
from scrapers.site import Site


class ScraperInput(BaseModel):
    site_type: list[Site]
    user: User
    search_term: str | None = None
    google_search_term: str | None = None

    location: str | None = None
    locations: list[str] | None = None
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
