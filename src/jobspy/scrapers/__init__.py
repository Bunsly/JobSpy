from ..jobs import Enum, BaseModel, JobType, JobResponse, Country


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
    full_description: bool = False
    offset: int = 0
    linkedin_company_ids: list[int] | None = None

    results_wanted: int = 15


class Scraper:
    def __init__(self, site: Site, proxy: list[str] | None = None):
        self.site = site
        self.proxy = (lambda p: {"http": p, "https": p} if p else None)(proxy)

    def scrape(self, scraper_input: ScraperInput) -> JobResponse:
        ...
