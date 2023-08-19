from fastapi import APIRouter

from api.core.scrapers.indeed import IndeedScraper
from api.core.scrapers.ziprecruiter import ZipRecruiterScraper
from api.core.scrapers.linkedin import LinkedInScraper
from api.core.scrapers import ScraperInput, Site, JobResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])

SCRAPER_MAPPING = {
    Site.LINKEDIN: LinkedInScraper,
    Site.INDEED: IndeedScraper,
    Site.ZIP_RECRUITER: ZipRecruiterScraper,
}


@router.post("/", response_model=JobResponse)
async def scrape_jobs(scraper_input: ScraperInput):
    scraper_class = SCRAPER_MAPPING[scraper_input.site_type]
    scraper = scraper_class()

    job_response = scraper.scrape(scraper_input)

    return job_response
