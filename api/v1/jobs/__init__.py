from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter

from api.core.scrapers.indeed import IndeedScraper
from api.core.scrapers.ziprecruiter import ZipRecruiterScraper
from api.core.scrapers.linkedin import LinkedInScraper
from api.core.scrapers import ScraperInput, Site, JobResponse
from typing import List, Dict, Tuple

router = APIRouter(prefix="/jobs", tags=["jobs"])

SCRAPER_MAPPING = {
    Site.LINKEDIN: LinkedInScraper,
    Site.INDEED: IndeedScraper,
    Site.ZIP_RECRUITER: ZipRecruiterScraper,
}


@router.post("/")
async def scrape_jobs(scraper_input: ScraperInput) -> Dict[str, JobResponse]:
    """
    Asynchronously scrapes job data from multiple job sites.
    :param scraper_input:
    :return: Dict[str, JobResponse]: where each key is a site
    """
    def scrape_site(site: Site) -> Tuple[str, JobResponse]:
        scraper_class = SCRAPER_MAPPING[site]
        scraper = scraper_class()
        scraped_data = scraper.scrape(scraper_input)
        return (site.value, scraped_data)

    with ThreadPoolExecutor() as executor:
        resp_dict = {site: resp for site, resp in executor.map(scrape_site, scraper_input.site_type)}

    return resp_dict

