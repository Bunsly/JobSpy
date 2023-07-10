from pydantic import BaseModel
from enum import Enum
from ..jobs import JobResponse, JobPost


class Site(Enum):
    LINKEDIN = "linkedin"
    INDEED = "indeed"
    ZIP_RECRUITER = "zip_recruiter"


class ScraperInput(BaseModel):
    site_type: Site

    search_term: str
    location: str
    distance: int = 25

    results_wanted: int = 15  #: TODO: implement


class Scraper:  #: to be used as a child class
    def __init__(self, site: Site):
        self.site = site

    def scrape(self, scraper_input: ScraperInput) -> JobResponse: ...
