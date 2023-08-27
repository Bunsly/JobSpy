import io
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from concurrent.futures import ThreadPoolExecutor

from api.core.scrapers.indeed import IndeedScraper
from api.core.scrapers.ziprecruiter import ZipRecruiterScraper
from api.core.scrapers.linkedin import LinkedInScraper
from api.core.formatters.csv import CSVFormatter, generate_filename
from api.core.scrapers import (
    ScraperInput,
    Site,
    JobResponse,
    OutputFormat,
    ScraperResponse,
)
from typing import List, Dict, Tuple, Union

router = APIRouter(prefix="/jobs", tags=["jobs"])

SCRAPER_MAPPING = {
    Site.LINKEDIN: LinkedInScraper,
    Site.INDEED: IndeedScraper,
    Site.ZIP_RECRUITER: ZipRecruiterScraper,
}


@router.post("/")
async def scrape_jobs(scraper_input: ScraperInput) -> ScraperResponse:
    """
    Asynchronously scrapes job data from multiple job sites.
    :param scraper_input:
    :return: scraper_response
    """

    def scrape_site(site: Site) -> Tuple[str, JobResponse]:
        scraper_class = SCRAPER_MAPPING[site]
        scraper = scraper_class()
        scraped_data: JobResponse = scraper.scrape(scraper_input)
        return (site.value, scraped_data)

    with ThreadPoolExecutor() as executor:
        results = dict(executor.map(scrape_site, scraper_input.site_type))

    scraper_response = ScraperResponse(**results)

    if scraper_input.output_format == OutputFormat.CSV:
        csv_output = CSVFormatter.format(scraper_response)
        response = StreamingResponse(csv_output, media_type="text/csv")
        response.headers[
            "Content-Disposition"
        ] = f"attachment; filename={generate_filename()}"
        return response

    return scraper_response
