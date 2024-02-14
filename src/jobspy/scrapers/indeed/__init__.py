"""
jobspy.scrapers.indeed
~~~~~~~~~~~~~~~~~~~

This module contains routines to scrape Indeed.
"""
import re
import math
import json
import requests
from typing import Any
from datetime import datetime

from bs4 import BeautifulSoup
from bs4.element import Tag
from concurrent.futures import ThreadPoolExecutor, Future

from ..exceptions import IndeedException
from ..utils import (
    count_urgent_words,
    extract_emails_from_text,
    create_session,
    get_enum_from_job_type,
    markdown_converter,
    logger
)
from ...jobs import (
    JobPost,
    Compensation,
    CompensationInterval,
    Location,
    JobResponse,
    JobType,
    DescriptionFormat
)
from .. import Scraper, ScraperInput, Site


class IndeedScraper(Scraper):
    def __init__(self, proxy: str | None = None):
        """
        Initializes IndeedScraper with the Indeed job search url
        """
        self.scraper_input = None
        self.jobs_per_page = 25
        self.num_workers = 10
        self.seen_urls = set()
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
        job_list = self._scrape_page()
        pages_processed = 1

        while len(self.seen_urls) < scraper_input.results_wanted:
            pages_to_process = math.ceil((scraper_input.results_wanted - len(self.seen_urls)) / self.jobs_per_page)
            new_jobs = False

            with ThreadPoolExecutor(max_workers=10) as executor:
                futures: list[Future] = [
                    executor.submit(self._scrape_page, page + pages_processed)
                    for page in range(pages_to_process)
                ]

                for future in futures:
                    jobs = future.result()
                    if jobs:
                        job_list += jobs
                        new_jobs = True
                    if len(self.seen_urls) >= scraper_input.results_wanted:
                        break

            pages_processed += pages_to_process
            if not new_jobs:
                break


        if len(self.seen_urls) > scraper_input.results_wanted:
            job_list = job_list[:scraper_input.results_wanted]

        return JobResponse(jobs=job_list)

    def _scrape_page(self, page: int=0) -> list[JobPost]:
        """
        Scrapes a page of Indeed for jobs with scraper_input criteria
        :param page:
        :return: jobs found on page, total number of jobs found for search
        """
        job_list = []
        domain = self.scraper_input.country.indeed_domain_value
        self.base_url = f"https://{domain}.indeed.com"

        try:
            session = create_session(self.proxy)
            response = session.get(
                f"{self.base_url}/m/jobs",
                headers=self.headers,
                params=self._add_params(page),
            )
            if response.status_code not in range(200, 400):
                if response.status_code == 429:
                    logger.error(f'429 Response - Blocked by Indeed for too many requests')
                else:
                    logger.error(f'Indeed response status code {response.status_code}')
                return job_list

        except Exception as e:
            if "Proxy responded with" in str(e):
                logger.error(f'Indeed: Bad proxy')
            else:
                logger.error(f'Indeed: {str(e)}')
            return job_list

        soup = BeautifulSoup(response.content, "html.parser")
        if "did not match any jobs" in response.text:
            return job_list

        jobs = IndeedScraper._parse_jobs(soup)
        if (
            not jobs.get("metaData", {})
            .get("mosaicProviderJobCardsModel", {})
            .get("results")
        ):
            raise IndeedException("No jobs found.")

        jobs = jobs["metaData"]["mosaicProviderJobCardsModel"]["results"]
        job_keys = [job['jobkey'] for job in jobs]
        jobs_detailed = self._get_job_details(job_keys)

        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            job_results: list[Future] = [
                executor.submit(self._process_job, job, job_detailed['job']) for job, job_detailed in zip(jobs, jobs_detailed)
            ]

        job_list = [result.result() for result in job_results if result.result()]

        return job_list

    def _process_job(self, job: dict, job_detailed: dict) -> JobPost | None:
        job_url = f'{self.base_url}/m/jobs/viewjob?jk={job["jobkey"]}'
        job_url_client = f'{self.base_url}/viewjob?jk={job["jobkey"]}'
        if job_url in self.seen_urls:
            return None
        self.seen_urls.add(job_url)
        description = job_detailed['description']['html']
        description = markdown_converter(description) if self.scraper_input.description_format == DescriptionFormat.MARKDOWN else description
        job_type = self._get_job_type(job)
        timestamp_seconds = job["pubDate"] / 1000
        date_posted = datetime.fromtimestamp(timestamp_seconds)
        date_posted = date_posted.strftime("%Y-%m-%d")
        return JobPost(
            title=job["normTitle"],
            description=description,
            company_name=job["company"],
            company_url=f"{self.base_url}{job_detailed['employer']['relativeCompanyPageUrl']}" if job_detailed[
                'employer'] else None,
            location=Location(
                city=job.get("jobLocationCity"),
                state=job.get("jobLocationState"),
                country=self.scraper_input.country,
            ),
            job_type=job_type,
            compensation=self._get_compensation(job, job_detailed),
            date_posted=date_posted,
            job_url=job_url_client,
            emails=extract_emails_from_text(description) if description else None,
            num_urgent_words=count_urgent_words(description) if description else None,
            is_remote=self._is_job_remote(job, job_detailed, description)
        )

    def _get_job_details(self, job_keys: list[str]) -> dict:
        """
        Queries the GraphQL endpoint for detailed job information for the given job keys.
        """
        job_keys_gql = '[' + ', '.join(f'"{key}"' for key in job_keys) + ']'
        payload = dict(self.api_payload)
        payload["query"] = self.api_payload["query"].format(job_keys_gql=job_keys_gql)
        response = requests.post(self.api_url, headers=self.api_headers, json=payload, proxies=self.proxy)
        if response.status_code == 200:
            return response.json()['data']['jobData']['results']
        else:
            return {}

    def _add_params(self, page: int) -> dict[str, str | Any]:
        fromage = max(self.scraper_input.hours_old // 24, 1) if self.scraper_input.hours_old else None
        params = {
            "q": self.scraper_input.search_term,
            "l": self.scraper_input.location if self.scraper_input.location else self.scraper_input.country.value[0].split(',')[-1],
            "filter": 0,
            "start": self.scraper_input.offset + page * 10,
            "sort": "date",
            "fromage": fromage,
        }
        if self.scraper_input.distance:
            params["radius"] = self.scraper_input.distance

        sc_values = []
        if self.scraper_input.is_remote:
            sc_values.append("attr(DSQF7)")
        if self.scraper_input.job_type:
            sc_values.append("jt({})".format(self.scraper_input.job_type.value[0]))

        if sc_values:
            params["sc"] = "0kf:" + "".join(sc_values) + ";"

        if self.scraper_input.easy_apply:
            params['iafilter'] = 1

        return params

    @staticmethod
    def _get_job_type(job: dict) -> list[JobType] | None:
        """
        Parses the job to get list of job types
        :param job:
        :return:
        """
        job_types: list[JobType] = []
        for taxonomy in job["taxonomyAttributes"]:
            if taxonomy["label"] == "job-types":
                for i in range(len(taxonomy["attributes"])):
                    label = taxonomy["attributes"][i].get("label")
                    if label:
                        job_type_str = label.replace("-", "").replace(" ", "").lower()
                        job_type = get_enum_from_job_type(job_type_str)
                        if job_type:
                            job_types.append(job_type)
        return job_types

    @staticmethod
    def _get_compensation(job: dict, job_detailed: dict) -> Compensation:
        """
        Parses the job to get
        :param job:
        :param job_detailed:
        :return: compensation object
        """
        comp = job_detailed['compensation']['baseSalary']
        if comp:
            interval = IndeedScraper._get_correct_interval(comp['unitOfWork'])
            if interval:
                return Compensation(
                    interval=interval,
                    min_amount=round(comp['range'].get('min'), 2) if comp['range'].get('min') is not None else None,
                    max_amount=round(comp['range'].get('max'), 2) if comp['range'].get('max') is not None else None,
                    currency=job_detailed['compensation']['currencyCode']
                )

        extracted_salary = job.get("extractedSalary")
        compensation = None
        if extracted_salary:
            salary_snippet = job.get("salarySnippet")
            currency = salary_snippet.get("currency") if salary_snippet else None
            interval = (extracted_salary.get("type"),)
            if isinstance(interval, tuple):
                interval = interval[0]

            interval = interval.upper()
            if interval in CompensationInterval.__members__:
                compensation = Compensation(
                    interval=CompensationInterval[interval],
                    min_amount=int(extracted_salary.get("min")),
                    max_amount=int(extracted_salary.get("max")),
                    currency=currency,
                )
        return compensation

    @staticmethod
    def _parse_jobs(soup: BeautifulSoup) -> dict:
        """
        Parses the jobs from the soup object
        :param soup:
        :return: jobs
        """
        def find_mosaic_script() -> Tag | None:
            script_tags = soup.find_all("script")

            for tag in script_tags:
                if (
                    tag.string
                    and "mosaic.providerData" in tag.string
                    and "mosaic-provider-jobcards" in tag.string
                ):
                    return tag
            return None

        script_tag = find_mosaic_script()
        if script_tag:
            script_str = script_tag.string
            pattern = r'window.mosaic.providerData\["mosaic-provider-jobcards"\]\s*=\s*({.*?});'
            p = re.compile(pattern, re.DOTALL)
            m = p.search(script_str)
            if m:
                jobs = json.loads(m.group(1).strip())
                return jobs
            else:
                raise IndeedException("Could not find mosaic provider job cards data")
        else:
            raise IndeedException(
                "Could not find any results for the search"
            )

    @staticmethod
    def _is_job_remote(job: dict, job_detailed: dict, description: str) -> bool:
        remote_keywords = ['remote', 'work from home', 'wfh']
        is_remote_in_attributes = any(
            any(keyword in attr['label'].lower() for keyword in remote_keywords)
            for attr in job_detailed['attributes']
        )
        is_remote_in_description = any(keyword in description.lower() for keyword in remote_keywords)
        is_remote_in_location = any(
            keyword in job_detailed['location']['formatted']['long'].lower()
            for keyword in remote_keywords
        )
        is_remote_in_taxonomy = any(
            taxonomy["label"] == "remote" and len(taxonomy["attributes"]) > 0
            for taxonomy in job.get("taxonomyAttributes", [])
        )
        return is_remote_in_attributes or is_remote_in_description or is_remote_in_location or is_remote_in_taxonomy

    @staticmethod
    def _get_correct_interval(interval: str) -> CompensationInterval:
        interval_mapping = {
            "DAY": "DAILY",
            "YEAR": "YEARLY",
            "HOUR": "HOURLY",
            "WEEK": "WEEKLY",
            "MONTH": "MONTHLY"
        }
        mapped_interval = interval_mapping.get(interval.upper(), None)
        if mapped_interval and mapped_interval in CompensationInterval.__members__:
            return CompensationInterval[mapped_interval]
        else:
            raise ValueError(f"Unsupported interval: {interval}")

    headers =  {
      'Host': 'www.indeed.com',
      'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'sec-fetch-site': 'same-origin',
      'sec-fetch-dest': 'document',
      'accept-language': 'en-US,en;q=0.9',
      'sec-fetch-mode': 'navigate',
      'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Indeed App 192.0',
      'referer': 'https://www.indeed.com/m/jobs?q=software%20intern&l=Dallas%2C%20TX&from=serpso&rq=1&rsIdx=3',
    }
    api_headers = {
        'Host': 'apis.indeed.com',
        'content-type': 'application/json',
        'indeed-api-key': '161092c2017b5bbab13edb12461a62d5a833871e7cad6d9d475304573de67ac8',
        'accept': 'application/json',
        'indeed-locale': 'en-US',
        'accept-language': 'en-US,en;q=0.9',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Indeed App 193.1',
        'indeed-app-info': 'appv=193.1; appid=com.indeed.jobsearch; osv=16.6.1; os=ios; dtype=phone',
        'indeed-co': 'US',
    }
    api_payload = {
        "query": """
        query GetJobData {{
          jobData(input: {{
            jobKeys: {job_keys_gql}
          }}) {{
            results {{
              job {{
                key
                title
                description {{
                  html
                }}
                location {{
                  countryName
                  countryCode
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
                  label
                }}
                employer {{
                  relativeCompanyPageUrl
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
    }
