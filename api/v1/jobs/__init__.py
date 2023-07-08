from fastapi import APIRouter

from api.core.scrapers.indeed import IndeedScraper
from api.core.scrapers import ScraperInput
from api.core.jobs import JobResponse

router = APIRouter(prefix="/jobs")


@router.get("/")
async def scrape_jobs(search_term: str, location: str, page: int = None):
    scraper = IndeedScraper()

    scraper_input = ScraperInput(search_term=search_term, location=location, page=page)
    job_response = scraper.scrape(scraper_input)
    return job_response
