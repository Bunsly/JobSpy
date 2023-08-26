from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter

from api.core.scrapers.indeed import IndeedScraper
from api.core.scrapers.ziprecruiter import ZipRecruiterScraper
from api.core.scrapers.linkedin import LinkedInScraper
from api.core.scrapers import ScraperInput, Site, JobResponse
from typing import List

router = APIRouter(prefix="/jobs", tags=["jobs"])

SCRAPER_MAPPING = {
    Site.LINKEDIN: LinkedInScraper,
    Site.INDEED: IndeedScraper,
    Site.ZIP_RECRUITER: ZipRecruiterScraper,
}


@router.post("/", response_model=List[JobResponse])
async def scrape_jobs(scraper_input: ScraperInput) -> List[JobResponse]:
    def scrape_site(site: str) -> JobResponse:
        scraper_class = SCRAPER_MAPPING[site]
        scraper = scraper_class()
        return scraper.scrape(scraper_input)

    with ThreadPoolExecutor() as executor:
        resp = list(executor.map(scrape_site, scraper_input.site_type))

    return resp
