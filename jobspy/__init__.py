from __future__ import annotations

import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
from pydantic import ValidationError

from jobspy.bayt import Bayt
from jobspy.bdjobs import BDJobs
from jobspy.glassdoor import Glassdoor
from jobspy.google import Google
from jobspy.hellowork import HelloWork
from jobspy.indeed import Indeed
from jobspy.linkedin import LinkedIn
from jobspy.model import (
    Country,
    JobResponse,
    Location,
    ScraperInput,
    Site,
)
from jobspy.naukri import Naukri
from jobspy.util import (
    configure_logging,
    convert_to_annual,
    desired_order,
    extract_salary,
)
from jobspy.ziprecruiter import ZipRecruiter

SCRAPER_MAPPING = {
    Site.LINKEDIN: LinkedIn,
    Site.INDEED: Indeed,
    Site.ZIP_RECRUITER: ZipRecruiter,
    Site.GLASSDOOR: Glassdoor,
    Site.GOOGLE: Google,
    Site.BAYT: Bayt,
    Site.NAUKRI: Naukri,
    Site.BDJOBS: BDJobs,
    Site.HELLOWORK: HelloWork,
}


def scrape_jobs(
    site_name: str | list[str] | Site | list[Site] | None = None,
    search_term: str | None = None,
    google_search_term: str | None = None,
    location: str | None = None,
    distance: int | None = 50,
    is_remote: bool | None = False,
    job_type: str | None = None,
    easy_apply: bool | None = None,
    results_wanted: int | None = 15,
    country_indeed: str | None = "usa",
    proxies: list[str] | str | None = None,
    ca_cert: str | None = None,
    description_format: str | None = "markdown",
    linkedin_fetch_description: bool | None = False,
    linkedin_company_ids: list[int] | None = None,
    offset: int | None = 0,
    hours_old: int | None = None,
    enforce_annual_salary: bool | None = False,
    verbose: int | None = 1,
    user_agent: str | None = None,
    fetch_description: bool | None = False,
) -> pd.DataFrame:
    """
    Scrapes job data from job boards concurrently
    :param linkedin_fetch_description: Deprecated since 1.2.0: use fetch_description;
        will be removed in 2.0.
    :return: Pandas DataFrame containing job data
    :raises ValueError: an argument is invalid
    """
    arguments = dict(locals())
    try:
        scraper_input = ScraperInput.model_validate(
            {
                name: value
                for name, value in arguments.items()
                if not (value is None or isinstance(value, str) and not value)
            }
        )
    except ValidationError as e:
        messages = []
        for error in e.errors():
            name, value = error["loc"][0], error["input"]
            shown = type(value).__name__ if name == "proxies" else repr(value)
            messages.append(f"Invalid {name}: {shown}. {error['msg']}")
        raise ValueError("; ".join(messages)) from None
    if scraper_input.linkedin_fetch_description:
        warnings.warn(
            "linkedin_fetch_description is deprecated; use fetch_description",
            DeprecationWarning,
            stacklevel=2,
        )
    configure_logging(None if verbose is None else scraper_input.verbose)

    def scrape_site(site: Site) -> tuple[str, JobResponse]:
        scraper = SCRAPER_MAPPING[site]()
        scraped_data: JobResponse = scraper.scrape(scraper_input)
        scraper.log.info("finished scraping")
        return site.value, scraped_data

    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(scrape_site, site)
            for site in dict.fromkeys(scraper_input.site_name)
        ]
        site_to_jobs_dict = dict(future.result() for future in as_completed(futures))

    rows = []
    for site, job_response in site_to_jobs_dict.items():
        for job in job_response.jobs:
            job_data = job.model_dump()
            job_data["site"] = site
            job_data["company"] = job_data["company_name"]
            job_data["job_type"] = (
                ", ".join(job_type.value for job_type in job_data["job_type"])
                if job_data["job_type"]
                else None
            )
            for name in ("emails", "skills"):
                job_data[name] = ", ".join(job_data[name]) if job_data[name] else None
            if job_data["location"]:
                job_data["location"] = Location(
                    **job_data["location"]
                ).display_location()

            job_data |= dict.fromkeys(
                ("interval", "min_amount", "max_amount", "currency", "salary_source")
            )
            if compensation := job_data["compensation"]:
                interval = compensation.pop("interval")
                job_data |= compensation
                job_data["interval"] = interval.value if interval else None
                job_data["salary_source"] = "direct_data"
                if scraper_input.enforce_annual_salary and job_data["interval"] not in (
                    None,
                    "yearly",
                ):
                    convert_to_annual(job_data)
            elif scraper_input.country_indeed == Country.USA:
                (
                    job_data["interval"],
                    job_data["min_amount"],
                    job_data["max_amount"],
                    job_data["currency"],
                ) = extract_salary(
                    job_data["description"],
                    enforce_annual_salary=scraper_input.enforce_annual_salary,
                )
                job_data["salary_source"] = "description"
            if not (job_data["min_amount"] or job_data["max_amount"]):
                job_data["salary_source"] = None
            rows.append(job_data)

    if not rows:
        return pd.DataFrame()
    jobs_df = pd.DataFrame(rows, columns=desired_order)
    return jobs_df.sort_values(
        by=["site", "date_posted"], ascending=[True, False]
    ).reset_index(drop=True)
