import io
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from concurrent.futures import ThreadPoolExecutor

from api.core.scrapers.indeed import IndeedScraper
from api.core.scrapers.ziprecruiter import ZipRecruiterScraper
from api.core.scrapers.linkedin import LinkedInScraper
from api.core.formatters.csv import CSVFormatter
from api.core.scrapers import (
    ScraperInput,
    Site,
    JobResponse,
    OutputFormat,
    CommonResponse,
)
from typing import List, Dict, Tuple, Union

router = APIRouter(prefix="/jobs", tags=["jobs"])

SCRAPER_MAPPING = {
    Site.LINKEDIN: LinkedInScraper,
    Site.INDEED: IndeedScraper,
    Site.ZIP_RECRUITER: ZipRecruiterScraper,
}


@router.post("/")
async def scrape_jobs(scraper_input: ScraperInput) -> CommonResponse:
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

    scraper_response = CommonResponse(status="JSON response success", **results)

    if scraper_input.output_format == OutputFormat.CSV:
        csv_output = CSVFormatter.format(scraper_response)
        response = StreamingResponse(csv_output, media_type="text/csv")
        response.headers[
            "Content-Disposition"
        ] = f"attachment; filename={CSVFormatter.generate_filename()}"
        return response

    elif scraper_input.output_format == OutputFormat.GSHEET:
        csv_output = CSVFormatter.format(scraper_response)
        try:
            CSVFormatter.upload_to_google_sheet(csv_output)
            return CommonResponse(status="Successfully uploaded to Google Sheets")

        except Exception as e:
            return CommonResponse(
                status="Failed to upload to Google Sheet", error=str(e)
            )

    else:
        return scraper_response
