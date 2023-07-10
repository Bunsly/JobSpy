from fastapi import APIRouter, Depends

from api.core.scrapers.indeed import IndeedScraper
from api.core.scrapers.ziprecruiter import ZipRecruiterScraper
from api.core.scrapers.linkedin import LinkedInScraper
from api.core.scrapers import ScraperInput, Site

router = APIRouter(prefix="/jobs")

SCRAPER_MAPPING = {
    Site.LINKEDIN: LinkedInScraper,
    Site.INDEED: IndeedScraper,
    Site.ZIP_RECRUITER: ZipRecruiterScraper,
}


@router.get("/")
async def scrape_jobs(
    site_type: Site, search_term: str, location: str, page: int = 1, distance: int = 25
):
    scraper_class = SCRAPER_MAPPING[site_type]
    scraper = scraper_class()

    scraper_input = ScraperInput(
        search_term=search_term, location=location, page=page, distance=distance
    )
    job_response = scraper.scrape(scraper_input)

    return job_response
