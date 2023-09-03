from ..jobs import Enum, BaseModel, JobType, JobResponse
from typing import List, Dict, Optional, Any


class StatusException(Exception):
    def __init__(self, status_code: int):
        self.status_code = status_code


class Site(Enum):
    LINKEDIN = "linkedin"
    INDEED = "indeed"
    ZIP_RECRUITER = "zip_recruiter"


class ScraperInput(BaseModel):
    site_type: List[Site]
    search_term: str

    location: str = None
    distance: Optional[int] = None
    is_remote: bool = False
    job_type: Optional[JobType] = None
    easy_apply: bool = None  # linkedin

    results_wanted: int = 15


class CommonResponse(BaseModel):
    status: Optional[str]
    error: Optional[str]
    linkedin: Optional[Any] = None
    indeed: Optional[Any] = None
    zip_recruiter: Optional[Any] = None


class Scraper:
    def __init__(self, site: Site, url: str):
        self.site = site
        self.url = url

    def scrape(self, scraper_input: ScraperInput) -> JobResponse:
        ...
