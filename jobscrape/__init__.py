import pandas as pd
from typing import List, Dict, Tuple, Union

from concurrent.futures import ThreadPoolExecutor

from .core.jobs import JobType
from .core.scrapers.indeed import IndeedScraper
from .core.scrapers.ziprecruiter import ZipRecruiterScraper
from .core.scrapers.linkedin import LinkedInScraper
from .core.scrapers import (
    ScraperInput,
    Site,
    JobResponse,
    CommonResponse,
)


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
        distance=distance,
        is_remote=is_remote,
        job_type=job_type,
        easy_apply=easy_apply,
        results_wanted=results_wanted,
    )

    def scrape_site(site: Site) -> Tuple[str, JobResponse]:
        scraper_class = SCRAPER_MAPPING[site]
        scraper = scraper_class()
        scraped_data: JobResponse = scraper.scrape(scraper_input)

        return site.value, scraped_data

    results = {}
    for site in scraper_input.site_type:
        site_value, scraped_data = scrape_site(site)
        results[site_value] = scraped_data

    dfs = []

    for site, job_response in results.items():
        for job in job_response.jobs:
            data = job.dict()
            data['site'] = site

            # Formatting JobType
            data['job_type'] = data['job_type'].value if data['job_type'] else None

            # Formatting Location
            location_obj = data.get('location')
            if location_obj and isinstance(location_obj, dict):
                data['city'] = location_obj.get('city', '')
                data['state'] = location_obj.get('state', '')
                data['country'] = location_obj.get('country', 'USA')
            else:
                data['city'] = None
                data['state'] = None
                data['country'] = None

            # Formatting Compensation
            compensation_obj = data.get('compensation')
            if compensation_obj and isinstance(compensation_obj, dict):
                data['interval'] = compensation_obj.get('interval').value if compensation_obj.get('interval') else None
                data['min_amount'] = compensation_obj.get('min_amount')
                data['max_amount'] = compensation_obj.get('max_amount')
                data['currency'] = compensation_obj.get('currency', 'USD')
            else:
                data['interval'] = None
                data['min_amount'] = None
                data['max_amount'] = None
                data['currency'] = None

            job_df = pd.DataFrame([data])
            dfs.append(job_df)

    if dfs:
        df = pd.concat(dfs, ignore_index=True)
        desired_order = ['site', 'title', 'company_name', 'city', 'state','job_type',
                         'interval', 'min_amount', 'max_amount',  'job_url', 'description',]
        df = df[desired_order]
    else:
        df = pd.DataFrame()

    return df




