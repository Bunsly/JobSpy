from concurrent.futures import ThreadPoolExecutor

from .core.scrapers.indeed import IndeedScraper
from .core.scrapers.ziprecruiter import ZipRecruiterScraper
from .core.scrapers.linkedin import LinkedInScraper
from .core.scrapers import (
    ScraperInput,
    Site,
    JobResponse,
)

import pandas as pd
from .core.jobs import JobType
from typing import List, Tuple

SCRAPER_MAPPING = {
    Site.LINKEDIN: LinkedInScraper,
    Site.INDEED: IndeedScraper,
    Site.ZIP_RECRUITER: ZipRecruiterScraper,
}


def _map_str_to_site(site_name: str) -> Site:
    return Site[site_name.upper()]


def scrape_jobs(
        site_name: str | Site | List[Site],
        search_term: str,

        location: str = "",
        distance: int = None,
        is_remote: bool = False,
        job_type: JobType = None,
        easy_apply: bool = False,  # linkedin
        results_wanted: int = 15
) -> pd.DataFrame:
    """
    Asynchronously scrapes job data from multiple job sites.
    :return: results_wanted: pandas dataframe containing job data
    """

    if type(site_name) == str:
        site_name = _map_str_to_site(site_name)

    site_type = [site_name] if type(site_name) == Site else site_name
    scraper_input = ScraperInput(
        site_type=site_type,
        search_term=search_term,
        location=location,
        is_remote=is_remote,
        easy_apply=easy_apply,
        results_wanted=results_wanted,
    )

    if distance:
        scraper_input.distance = distance

    if job_type:
        scraper_input.job_type = job_type

    def scrape_site(site: Site) -> Tuple[str, JobResponse]:
        scraper_class = SCRAPER_MAPPING[site]
        scraper = scraper_class()
        scraped_data: JobResponse = scraper.scrape(scraper_input)
        return site.value, scraped_data

    with ThreadPoolExecutor(max_workers=3) as executor:
        results = dict(executor.map(scrape_site, scraper_input.site_type))

    df = pd.DataFrame()

    for site in results:
        for job in results[site].jobs:
            data = job.json()

            data_df = pd.read_json(data, typ='series')
            data_df['site'] = site

            #: concat
            df = pd.concat([df, data_df], axis=1)

    return df


