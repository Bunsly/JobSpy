import pandas as pd
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from typing import Tuple, Optional

from .jobs import JobType, Location
from .scrapers.indeed import IndeedScraper
from .scrapers.ziprecruiter import ZipRecruiterScraper
from .scrapers.glassdoor import GlassdoorScraper
from .scrapers.linkedin import LinkedInScraper
from .scrapers import ScraperInput, Site, JobResponse, Country
from .scrapers.exceptions import (
    LinkedInException,
    IndeedException,
    ZipRecruiterException,
    GlassdoorException,
)

SCRAPER_MAPPING = {
    Site.LINKEDIN: LinkedInScraper,
    Site.INDEED: IndeedScraper,
    Site.ZIP_RECRUITER: ZipRecruiterScraper,
    Site.GLASSDOOR: GlassdoorScraper,
}


def _map_str_to_site(site_name: str) -> Site:
    return Site[site_name.upper()]


def scrape_jobs(
    site_name: str | list[str] | Site | list[Site],
    search_term: str,
    location: str = "",
    distance: int = None,
    is_remote: bool = False,
    job_type: str = None,
    easy_apply: bool = False,  # linkedin
    results_wanted: int = 15,
    country_indeed: str = "usa",
    hyperlinks: bool = False,
    proxy: Optional[str] = None,
    offset: Optional[int] = 0,
) -> pd.DataFrame:
    """
    Simultaneously scrapes job data from multiple job sites.
    :return: results_wanted: pandas dataframe containing job data
    """

    def get_enum_from_value(value_str):
        for job_type in JobType:
            if value_str in job_type.value:
                return job_type
        raise Exception(f"Invalid job type: {value_str}")

    job_type = get_enum_from_value(job_type) if job_type else None

    if type(site_name) == str:
        site_type = [_map_str_to_site(site_name)]
    else:  #: if type(site_name) == list
        site_type = [
            _map_str_to_site(site) if type(site) == str else site_name
            for site in site_name
        ]

    country_enum = Country.from_string(country_indeed)

    scraper_input = ScraperInput(
        site_type=site_type,
        country=country_enum,
        search_term=search_term,
        location=location,
        distance=distance,
        is_remote=is_remote,
        job_type=job_type,
        easy_apply=easy_apply,
        results_wanted=results_wanted,
        offset=offset,
    )

    def scrape_site(site: Site) -> Tuple[str, JobResponse]:
        scraper_class = SCRAPER_MAPPING[site]
        scraper = scraper_class(proxy=proxy)

        try:
            scraped_data: JobResponse = scraper.scrape(scraper_input)
        except (LinkedInException, IndeedException, ZipRecruiterException) as lie:
            raise lie
        except Exception as e:
            if site == Site.LINKEDIN:
                raise LinkedInException(str(e))
            if site == Site.INDEED:
                raise IndeedException(str(e))
            if site == Site.ZIP_RECRUITER:
                raise ZipRecruiterException(str(e))
            if site == Site.GLASSDOOR:
                raise GlassdoorException(str(e))
            else:
                raise e
        return site.value, scraped_data

    site_to_jobs_dict = {}

    def worker(site):
        site_val, scraped_info = scrape_site(site)
        return site_val, scraped_info

    with ThreadPoolExecutor() as executor:
        future_to_site = {
            executor.submit(worker, site): site for site in scraper_input.site_type
        }

        for future in concurrent.futures.as_completed(future_to_site):
            site_value, scraped_data = future.result()
            site_to_jobs_dict[site_value] = scraped_data

    jobs_dfs: list[pd.DataFrame] = []

    for site, job_response in site_to_jobs_dict.items():
        for job in job_response.jobs:
            job_data = job.dict()
            job_data[
                "job_url_hyper"
            ] = f'<a href="{job_data["job_url"]}">{job_data["job_url"]}</a>'
            job_data["site"] = site
            job_data["company"] = job_data["company_name"]
            job_data["job_type"] = (
                ", ".join(job_type.value[0] for job_type in job_data["job_type"])
                if job_data["job_type"]
                else None
            )
            job_data["emails"] = (
                ", ".join(job_data["emails"]) if job_data["emails"] else None
            )
            if job_data["location"]:
                job_data["location"] = Location(
                    **job_data["location"]
                ).display_location()

            compensation_obj = job_data.get("compensation")
            if compensation_obj and isinstance(compensation_obj, dict):
                job_data["interval"] = (
                    compensation_obj.get("interval").value
                    if compensation_obj.get("interval")
                    else None
                )
                job_data["min_amount"] = compensation_obj.get("min_amount")
                job_data["max_amount"] = compensation_obj.get("max_amount")
                job_data["currency"] = compensation_obj.get("currency", "USD")
            else:
                job_data["interval"] = None
                job_data["min_amount"] = None
                job_data["max_amount"] = None
                job_data["currency"] = None

            job_df = pd.DataFrame([job_data])
            jobs_dfs.append(job_df)

    if jobs_dfs:
        jobs_df = pd.concat(jobs_dfs, ignore_index=True)
        desired_order: list[str] = [
            "job_url_hyper" if hyperlinks else "job_url",
            "site",
            "title",
            "company",
            "company_url",
            "location",
            "job_type",
            "date_posted",
            "interval",
            "min_amount",
            "max_amount",
            "currency",
            "is_remote",
            "num_urgent_words",
            "benefits",
            "emails",
            "description",
        ]
        jobs_formatted_df = jobs_df[desired_order]
    else:
        jobs_formatted_df = pd.DataFrame()

    return jobs_formatted_df
