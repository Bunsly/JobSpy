from pydantic import BaseModel
from enum import Enum
from ..jobs import JobResponse


class Site(Enum):
    LINKEDIN = "linkedin"
    INDEED = "indeed"
    ZIP_RECRUITER = "zip_recruiter"


class ScraperInput(BaseModel):
    location: str
    search_term: str
    distance: int = 25

    page: int = 1


class Scraper:  #: to be used as a child class
    def __init__(self, site: Site):
        self.site = site

    def scrape(self, scraper_input: ScraperInput) -> JobResponse:
        ...
