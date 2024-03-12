"""
jobspy.scrapers.indeed
~~~~~~~~~~~~~~~~~~~

This module contains routines to scrape Indeed.
"""

from __future__ import annotations

import math
from typing import Tuple
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, Future

import requests

from .. import Scraper, ScraperInput, Site
from ..utils import (
    extract_emails_from_text,
    get_enum_from_job_type,
    markdown_converter,
    logger,
)
from ...jobs import (
    JobPost,
    Compensation,
    CompensationInterval,
    Location,
    JobResponse,
    JobType,
    DescriptionFormat,
)


class IndeedScraper(Scraper):
    def __init__(self, proxy: str | None = None):
        """
        Initializes IndeedScraper with the Indeed API url
        """
        self.scraper_input = None
        self.jobs_per_page = 100
        self.num_workers = 10
        self.seen_urls = set()
        self.headers = None
        self.api_country_code = None
        self.base_url = None
        self.api_url = "https://apis.indeed.com/graphql"
        site = Site(Site.INDEED)
        super().__init__(site, proxy=proxy)

    def scrape(self, scraper_input: ScraperInput) -> JobResponse:
        """
        Scrapes Indeed for jobs with scraper_input criteria
        :param scraper_input:
        :return: job_response
        """
        self.scraper_input = scraper_input
        domain, self.api_country_code = self.scraper_input.country.indeed_domain_value
        self.base_url = f"https://{domain}.indeed.com"
        self.headers = self.api_headers.copy()
        self.headers["indeed-co"] = self.scraper_input.country.indeed_domain_value
        job_list = []
        page = 1

        cursor = None
        offset_pages = math.ceil(self.scraper_input.offset / 100)
        for _ in range(offset_pages):
            logger.info(f"Indeed skipping search page: {page}")
            __, cursor = self._scrape_page(cursor)
            if not __:
                logger.info(f"Indeed found no jobs on page: {page}")
                break

        while len(self.seen_urls) < scraper_input.results_wanted:
            logger.info(f"Indeed search page: {page}")
            jobs, cursor = self._scrape_page(cursor)
            if not jobs:
                logger.info(f"Indeed found no jobs on page: {page}")
                break
            job_list += jobs
            page += 1
        return JobResponse(jobs=job_list[: scraper_input.results_wanted])

    def _scrape_page(self, cursor: str | None) -> Tuple[list[JobPost], str | None]:
        """
        Scrapes a page of Indeed for jobs with scraper_input criteria
        :param cursor:
        :return: jobs found on page, next page cursor
        """
        jobs = []
        new_cursor = None
        filters = self._build_filters()
        query = self.job_search_query.format(
            what=(
                f'what: "{self.scraper_input.search_term}"'
                if self.scraper_input.search_term
                else ""
            ),
            location=(
                f'location: {{where: "{self.scraper_input.location}", radius: {self.scraper_input.distance}, radiusUnit: MILES}}'
                if self.scraper_input.location
                else ""
            ),
            dateOnIndeed=self.scraper_input.hours_old,
            cursor=f'cursor: "{cursor}"' if cursor else "",
            filters=filters,
        )
        payload = {
            "query": query,
        }
        api_headers = self.api_headers.copy()
        api_headers["indeed-co"] = self.api_country_code
        response = requests.post(
            self.api_url,
            headers=api_headers,
            json=payload,
            proxies=self.proxy,
            timeout=10,
        )
        if response.status_code != 200:
            logger.info(
                f"Indeed responded with status code: {response.status_code} (submit GitHub issue if this appears to be a beg)"
            )
            return jobs, new_cursor
        data = response.json()
        jobs = data["data"]["jobSearch"]["results"]
        new_cursor = data["data"]["jobSearch"]["pageInfo"]["nextCursor"]

        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            job_results: list[Future] = [
                executor.submit(self._process_job, job["job"]) for job in jobs
            ]
        job_list = [result.result() for result in job_results if result.result()]
        return job_list, new_cursor

    def _build_filters(self):
        """
        Builds the filters dict for job type/is_remote. If hours_old is provided, composite filter for job_type/is_remote is not possible.
        IndeedApply: filters: { keyword: { field: "indeedApplyScope", keys: ["DESKTOP"] } }
        """
        filters_str = ""
        if self.scraper_input.hours_old:
            filters_str = """
            filters: {{
                date: {{
                  field: "dateOnIndeed",
                  start: "{start}h"
                }}
            }}
            """.format(
                start=self.scraper_input.hours_old
            )
        elif self.scraper_input.easy_apply:
            filters_str = """
            filters: {
                keyword: {
                  field: "indeedApplyScope",
                  keys: ["DESKTOP"]
                }
            }
            """
        elif self.scraper_input.job_type or self.scraper_input.is_remote:
            job_type_key_mapping = {
                JobType.FULL_TIME: "CF3CP",
                JobType.PART_TIME: "75GKK",
                JobType.CONTRACT: "NJXCK",
                JobType.INTERNSHIP: "VDTG7",
            }

            keys = []
            if self.scraper_input.job_type:
                key = job_type_key_mapping[self.scraper_input.job_type]
                keys.append(key)

            if self.scraper_input.is_remote:
                keys.append("DSQF7")

            if keys:
                keys_str = '", "'.join(keys)  # Prepare your keys string
                filters_str = f"""
                filters: {{
                  composite: {{
                    filters: [{{
                      keyword: {{
                        field: "attributes",
                        keys: ["{keys_str}"]
                      }}
                    }}]
                  }}
                }}
                """
        return filters_str

    def _process_job(self, job: dict) -> JobPost | None:
        """
        Parses the job dict into JobPost model
        :param job: dict to parse
        :return: JobPost if it's a new job
        """
        job_url = f'{self.base_url}/viewjob?jk={job["key"]}'
        if job_url in self.seen_urls:
            return
        self.seen_urls.add(job_url)
        description = job["description"]["html"]
        if self.scraper_input.description_format == DescriptionFormat.MARKDOWN:
            description = markdown_converter(description)

        job_type = self._get_job_type(job["attributes"])
        timestamp_seconds = job["datePublished"] / 1000
        date_posted = datetime.fromtimestamp(timestamp_seconds).strftime("%Y-%m-%d")
        employer = job["employer"].get("dossier") if job["employer"] else None
        employer_details = employer.get("employerDetails", {}) if employer else {}
        rel_url = job["employer"]["relativeCompanyPageUrl"] if job["employer"] else None
        return JobPost(
            title=job["title"],
            description=description,
            company_name=job["employer"].get("name") if job.get("employer") else None,
            company_url=(f"{self.base_url}{rel_url}" if job["employer"] else None),
            company_url_direct=(
                employer["links"]["corporateWebsite"] if employer else None
            ),
            location=Location(
                city=job.get("location", {}).get("city"),
                state=job.get("location", {}).get("admin1Code"),
                country=job.get("location", {}).get("countryCode"),
            ),
            job_type=job_type,
            compensation=self._get_compensation(job),
            date_posted=date_posted,
            job_url=job_url,
            job_url_direct=(
                job["recruit"].get("viewJobUrl") if job.get("recruit") else None
            ),
            emails=extract_emails_from_text(description) if description else None,
            is_remote=self._is_job_remote(job, description),
            company_addresses=(
                employer_details["addresses"][0]
                if employer_details.get("addresses")
                else None
            ),
            company_industry=(
                employer_details["industry"]
                .replace("Iv1", "")
                .replace("_", " ")
                .title()
                if employer_details.get("industry")
                else None
            ),
            company_num_employees=employer_details.get("employeesLocalizedLabel"),
            company_revenue=employer_details.get("revenueLocalizedLabel"),
            company_description=employer_details.get("briefDescription"),
            ceo_name=employer_details.get("ceoName"),
            ceo_photo_url=employer_details.get("ceoPhotoUrl"),
            logo_photo_url=(
                employer["images"].get("squareLogoUrl")
                if employer and employer.get("images")
                else None
            ),
            banner_photo_url=(
                employer["images"].get("headerImageUrl")
                if employer and employer.get("images")
                else None
            ),
        )

    @staticmethod
    def _get_job_type(attributes: list) -> list[JobType]:
        """
        Parses the attributes to get list of job types
        :param attributes:
        :return: list of JobType
        """
        job_types: list[JobType] = []
        for attribute in attributes:
            job_type_str = attribute["label"].replace("-", "").replace(" ", "").lower()
            job_type = get_enum_from_job_type(job_type_str)
            if job_type:
                job_types.append(job_type)
        return job_types

    @staticmethod
    def _get_compensation(job: dict) -> Compensation | None:
        """
        Parses the job to get compensation
        :param job:
        :param job:
        :return: compensation object
        """
        comp = job["compensation"]["baseSalary"]
        if not comp:
            return None
        interval = IndeedScraper._get_compensation_interval(comp["unitOfWork"])
        if not interval:
            return None
        min_range = comp["range"].get("min")
        max_range = comp["range"].get("max")
        return Compensation(
            interval=interval,
            min_amount=round(min_range, 2) if min_range is not None else None,
            max_amount=round(max_range, 2) if max_range is not None else None,
            currency=job["compensation"]["currencyCode"],
        )

    @staticmethod
    def _is_job_remote(job: dict, description: str) -> bool:
        """
        Searches the description, location, and attributes to check if job is remote
        """
        remote_keywords = ["remote", "work from home", "wfh"]
        is_remote_in_attributes = any(
            any(keyword in attr["label"].lower() for keyword in remote_keywords)
            for attr in job["attributes"]
        )
        is_remote_in_description = any(
            keyword in description.lower() for keyword in remote_keywords
        )
        is_remote_in_location = any(
            keyword in job["location"]["formatted"]["long"].lower()
            for keyword in remote_keywords
        )
        return (
            is_remote_in_attributes or is_remote_in_description or is_remote_in_location
        )

    @staticmethod
    def _get_compensation_interval(interval: str) -> CompensationInterval:
        interval_mapping = {
            "DAY": "DAILY",
            "YEAR": "YEARLY",
            "HOUR": "HOURLY",
            "WEEK": "WEEKLY",
            "MONTH": "MONTHLY",
        }
        mapped_interval = interval_mapping.get(interval.upper(), None)
        if mapped_interval and mapped_interval in CompensationInterval.__members__:
            return CompensationInterval[mapped_interval]
        else:
            raise ValueError(f"Unsupported interval: {interval}")

    api_headers = {
        "Host": "apis.indeed.com",
        "content-type": "application/json",
        "indeed-api-key": "161092c2017b5bbab13edb12461a62d5a833871e7cad6d9d475304573de67ac8",
        "accept": "application/json",
        "indeed-locale": "en-US",
        "accept-language": "en-US,en;q=0.9",
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Indeed App 193.1",
        "indeed-app-info": "appv=193.1; appid=com.indeed.jobsearch; osv=16.6.1; os=ios; dtype=phone",
    }
    job_search_query = """
        query GetJobData {{
          jobSearch(
            {what}
            {location}
            includeSponsoredResults: NONE
            limit: 100
            sort: DATE
            {cursor}
            {filters}
          ) {{
            pageInfo {{
              nextCursor
            }}
            results {{
              trackingKey
              job {{
                key
                title
                datePublished
                dateOnIndeed
                description {{
                  html
                }}
                location {{
                  countryName
                  countryCode
                  admin1Code
                  city
                  postalCode
                  streetAddress
                  formatted {{
                    short
                    long
                  }}
                }}
                compensation {{
                  baseSalary {{
                    unitOfWork
                    range {{
                      ... on Range {{
                        min
                        max
                      }}
                    }}
                  }}
                  currencyCode
                }}
                attributes {{
                  key
                  label
                }}
                employer {{
                  relativeCompanyPageUrl
                  name
                  dossier {{
                      employerDetails {{
                        addresses
                        industry
                        employeesLocalizedLabel
                        revenueLocalizedLabel
                        briefDescription
                        ceoName
                        ceoPhotoUrl
                      }}
                      images {{
                            headerImageUrl
                            squareLogoUrl
                      }}
                      links {{
                        corporateWebsite
                    }}
                  }}
                }}
                recruit {{
                  viewJobUrl
                  detailedSalary
                  workSchedule
                }}
              }}
            }}
          }}
        }}
        """
