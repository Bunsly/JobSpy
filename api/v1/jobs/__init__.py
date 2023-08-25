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
async def scrape_jobs(scraper_input: ScraperInput) -> JobResponse:
    resp = []
    for site in scraper_input.site_type:
        scraper_class = SCRAPER_MAPPING[site]
        scraper = scraper_class()
        job_response = scraper.scrape(scraper_input)
        resp.append(job_response)

    return resp
