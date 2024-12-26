from __future__ import annotations
from threading import Lock

import pandas as pd
from typing import Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from .scrapers.site import Site

from .scrapers.goozali import GoozaliScraper

from .jobs import JobPost, JobType, Location
from .scrapers.utils import set_logger_level, extract_salary, create_logger
from .scrapers.indeed import IndeedScraper
from .scrapers.ziprecruiter import ZipRecruiterScraper
from .scrapers.glassdoor import GlassdoorScraper
from .scrapers.google import GoogleJobsScraper
from .scrapers.linkedin import LinkedInScraper
from .scrapers import SalarySource, ScraperInput, JobResponse, Country
from .scrapers.exceptions import (
    LinkedInException,
    IndeedException,
    ZipRecruiterException,
    GlassdoorException,
    GoogleJobsException,
)


def scrape_jobs(
    site_name: str | list[str] | Site | list[Site] | None = None,
    search_term: str | None = None,
    google_search_term: str | None = None,
    location: str | None = None,
    locations: list[str] | None = None,
    distance: int | None = 50,
    is_remote: bool = False,
    job_type: str | None = None,
    easy_apply: bool | None = None,
    results_wanted: int = 15,
    country_indeed: str = "usa",
    hyperlinks: bool = False,
    proxies: list[str] | str | None = None,
    ca_cert: str | None = None,
    description_format: str = "markdown",
    linkedin_fetch_description: bool | None = False,
    linkedin_company_ids: list[int] | None = None,
    offset: int | None = 0,
    hours_old: int = None,
    enforce_annual_salary: bool = False,
    verbose: int = 2,
    ** kwargs,
) -> pd.DataFrame:
    """
    Simultaneously scrapes job data from multiple job sites.
    :return: pandas dataframe containing job data
    """
    SCRAPER_MAPPING = {
        Site.LINKEDIN: LinkedInScraper,
        Site.INDEED: IndeedScraper,
        Site.ZIP_RECRUITER: ZipRecruiterScraper,
        Site.GLASSDOOR: GlassdoorScraper,
        Site.GOOGLE: GoogleJobsScraper,
        Site.GOOZALI: GoozaliScraper,
    }
    set_logger_level(verbose)

    def map_str_to_site(site_name: str) -> Site:
        return Site[site_name.upper()]

    def get_enum_from_value(value_str):
        for job_type in JobType:
            if value_str in job_type.value:
                return job_type
        raise Exception(f"Invalid job type: {value_str}")

    job_type = get_enum_from_value(job_type) if job_type else None

    def get_site_type():
        site_types = list(Site)
        if isinstance(site_name, str):
            site_types = [map_str_to_site(site_name)]
        elif isinstance(site_name, Site):
            site_types = [site_name]
        elif isinstance(site_name, list):
            site_types = [
                map_str_to_site(site) if isinstance(site, str) else site
                for site in site_name
            ]
        return site_types

    country_enum = Country.from_string(country_indeed)
    scraper_input = ScraperInput(
        site_type=get_site_type(),
        country=country_enum,
        search_term=search_term,
        google_search_term=google_search_term,
        location=location,
        locations=locations,
        distance=distance,
        is_remote=is_remote,
        job_type=job_type,
        easy_apply=easy_apply,
        description_format=description_format,
        linkedin_fetch_description=linkedin_fetch_description,
        results_wanted=results_wanted,
        linkedin_company_ids=linkedin_company_ids,
        offset=offset,
        hours_old=hours_old
    )

    def scrape_site(site: Site) -> Tuple[str, JobResponse]:
        scraper_class = SCRAPER_MAPPING[site]
        scraper = scraper_class(proxies=proxies, ca_cert=ca_cert)
        scraped_data: JobResponse = scraper.scrape(scraper_input)
        cap_name = site.value.capitalize()
        site_name = "ZipRecruiter" if cap_name == "Zip_recruiter" else cap_name
        create_logger(site_name).info(f"finished scraping")
        return site.value, scraped_data

    site_to_jobs_dict = {}
    merged_jobs: list[JobPost] = []
    lock = Lock()

    def worker(site):
        logger = create_logger(f"Worker {site}")
        logger.info("Starting")
        try:
            site_val, scraped_info = scrape_site(site)
            with lock:
                merged_jobs.extend(scraped_info.jobs)
            logger.info("Finished")
            return site_val, scraped_info
        except Exception as e:
            logger.error(f"Error: {e}")
            return None, None

    with ThreadPoolExecutor(max_workers=5) as executor:
        logger = create_logger("ThreadPoolExecutor")
        future_to_site = {
            executor.submit(worker, site): site for site in scraper_input.site_type
        }
        # An iterator over the given futures that yields each as it completes.
        for future in as_completed(future_to_site):
            try:
                site_value, scraped_data = future.result()
                if site_value and scraped_data:
                    site_to_jobs_dict[site_value] = scraped_data
            except Exception as e:
                logger.error(f"Future Error occurred: {e}")

    return merged_jobs
