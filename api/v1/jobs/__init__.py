from fastapi import APIRouter

from api.core.scrapers.indeed import IndeedScraper
from api.core.scrapers.ziprecruiter import ZipRecruiterScraper
from api.core.scrapers import ScraperInput
from api.core.jobs import JobResponse

router = APIRouter(prefix="/jobs")


@router.get("/")
async def scrape_jobs(
    site_type: str, search_term: str, location: str, page: int = None
):
    job_response = {"message": "site type not found"}
    if site_type == "indeed":
        indeed_scraper = IndeedScraper()
        scraper_input = ScraperInput(
            search_term=search_term, location=location, page=page
        )
        job_response = indeed_scraper.scrape(scraper_input)
    elif site_type == "zip":
        ziprecruiter_scraper = ZipRecruiterScraper()
        scraper_input = ScraperInput(
            search_term=search_term, location=location, page=page
        )
        job_response = ziprecruiter_scraper.scrape(scraper_input)

    return job_response
