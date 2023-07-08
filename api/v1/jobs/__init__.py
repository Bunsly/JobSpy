from fastapi import APIRouter

from api.core.scrapers.indeed import IndeedScraper
from api.core.scrapers.ziprecruiter import ZipRecruiterScraper
from api.core.scrapers.linkedin import LinkedInScraper
from api.core.scrapers import ScraperInput

router = APIRouter(prefix="/jobs")


@router.get("/")
async def scrape_jobs(
    site_type: str, search_term: str, location: str, page: int = None
):
    job_response = {"message": "site type not found"}

    scraper_dict = {
        "indeed": IndeedScraper,
        "linkedin": LinkedInScraper,
        "zip": ZipRecruiterScraper,
    }

    scraper_class = scraper_dict.get(site_type)
    if scraper_class:
        scraper = scraper_class()
        scraper_input = ScraperInput(
            search_term=search_term, location=location, page=page
        )
        job_response = scraper.scrape(scraper_input)

    return job_response
