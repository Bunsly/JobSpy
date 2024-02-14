"""
jobspy.scrapers.glassdoor
~~~~~~~~~~~~~~~~~~~

This module contains routines to scrape Glassdoor.
"""
import json
import requests
from typing import Optional
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from ..utils import count_urgent_words, extract_emails_from_text

from .. import Scraper, ScraperInput, Site
from ..exceptions import GlassdoorException
from ..utils import (
    create_session,
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


class GlassdoorScraper(Scraper):
    def __init__(self, proxy: Optional[str] = None):
        """
        Initializes GlassdoorScraper with the Glassdoor job search url
        """
        site = Site(Site.GLASSDOOR)
        super().__init__(site, proxy=proxy)

        self.base_url = None
        self.country = None
        self.session = None
        self.scraper_input = None
        self.jobs_per_page = 30
        self.seen_urls = set()

    def scrape(self, scraper_input: ScraperInput) -> JobResponse:
        """
        Scrapes Glassdoor for jobs with scraper_input criteria.
        :param scraper_input: Information about job search criteria.
        :return: JobResponse containing a list of jobs.
        """
        self.scraper_input = scraper_input
        self.scraper_input.results_wanted = min(900, scraper_input.results_wanted)
        self.base_url = self.scraper_input.country.get_url()

        location_id, location_type = self._get_location(
            scraper_input.location, scraper_input.is_remote
        )
        if location_type is None:
            return JobResponse(jobs=[])
        all_jobs: list[JobPost] = []
        cursor = None
        max_pages = 30
        self.session = create_session(self.proxy, is_tls=False, has_retry=True)
        self.session.get(self.base_url)

        try:
            for page in range(
                1 + (scraper_input.offset // self.jobs_per_page),
                min(
                    (scraper_input.results_wanted // self.jobs_per_page) + 2,
                    max_pages + 1,
                ),
            ):
                try:
                    jobs, cursor = self._fetch_jobs_page(
                        scraper_input, location_id, location_type, page, cursor
                    )
                    all_jobs.extend(jobs)
                    if len(all_jobs) >= scraper_input.results_wanted:
                        all_jobs = all_jobs[: scraper_input.results_wanted]
                        break
                except Exception as e:
                    raise GlassdoorException(str(e))
        except Exception as e:
            raise GlassdoorException(str(e))
        return JobResponse(jobs=all_jobs)

    def _fetch_jobs_page(
        self,
        scraper_input: ScraperInput,
        location_id: int,
        location_type: str,
        page_num: int,
        cursor: str | None,
    ) -> (list[JobPost], str | None):
        """
        Scrapes a page of Glassdoor for jobs with scraper_input criteria
        """
        self.scraper_input = scraper_input
        try:
            payload = self._add_payload(
                location_id, location_type, page_num, cursor
            )
            response = self.session.post(
                f"{self.base_url}/graph", headers=self.headers, timeout=10, data=payload
            )
            if response.status_code != 200:
                raise GlassdoorException(
                    f"bad response status code: {response.status_code}"
                )
            res_json = response.json()[0]
            if "errors" in res_json:
                raise ValueError("Error encountered in API response")
        except Exception as e:
            raise GlassdoorException(str(e))

        jobs_data = res_json["data"]["jobListings"]["jobListings"]

        jobs = []
        with ThreadPoolExecutor(max_workers=self.jobs_per_page) as executor:
            future_to_job_data = {executor.submit(self._process_job, job): job for job in jobs_data}
            for future in as_completed(future_to_job_data):
                try:
                    job_post = future.result()
                    if job_post:
                        jobs.append(job_post)
                except Exception as exc:
                    raise GlassdoorException(f'Glassdoor generated an exception: {exc}')

        return jobs, self.get_cursor_for_page(
            res_json["data"]["jobListings"]["paginationCursors"], page_num + 1
        )

    def _process_job(self, job_data):
        """
        Processes a single job and fetches its description.
        """
        job_id = job_data["jobview"]["job"]["listingId"]
        job_url = f'{self.base_url}job-listing/j?jl={job_id}'
        if job_url in self.seen_urls:
            return None
        self.seen_urls.add(job_url)
        job = job_data["jobview"]
        title = job["job"]["jobTitleText"]
        company_name = job["header"]["employerNameFromSearch"]
        company_id = job_data['jobview']['header']['employer']['id']
        location_name = job["header"].get("locationName", "")
        location_type = job["header"].get("locationType", "")
        age_in_days = job["header"].get("ageInDays")
        is_remote, location = False, None
        date_posted = (datetime.now() - timedelta(days=age_in_days)).date() if age_in_days is not None else None

        if location_type == "S":
            is_remote = True
        else:
            location = self.parse_location(location_name)

        compensation = self.parse_compensation(job["header"])
        try:
            description = self._fetch_job_description(job_id)
        except:
            description = None
        return JobPost(
            title=title,
            company_url=f"{self.base_url}Overview/W-EI_IE{company_id}.htm" if company_id else None,
            company_name=company_name,
            date_posted=date_posted,
            job_url=job_url,
            location=location,
            compensation=compensation,
            is_remote=is_remote,
            description=description,
            emails=extract_emails_from_text(description) if description else None,
            num_urgent_words=count_urgent_words(description) if description else None,
        )

    def _fetch_job_description(self, job_id):
        """
        Fetches the job description for a single job ID.
        """
        url = f"{self.base_url}/graph"
        body = [
            {
                "operationName": "JobDetailQuery",
                "variables": {
                    "jl": job_id,
                    "queryString": "q",
                    "pageTypeEnum": "SERP"
                },
                "query": """
                query JobDetailQuery($jl: Long!, $queryString: String, $pageTypeEnum: PageTypeEnum) {
                    jobview: jobView(
                        listingId: $jl
                        contextHolder: {queryString: $queryString, pageTypeEnum: $pageTypeEnum}
                    ) {
                        job {
                            description
                            __typename
                        }
                        __typename
                    }
                }
                """
            }
        ]
        res = requests.post(url, json=body, headers=self.headers)
        if res.status_code != 200:
            return None
        data = res.json()[0]
        desc = data['data']['jobview']['job']['description']
        return markdown_converter(desc) if self.scraper_input.description_format == DescriptionFormat.MARKDOWN else desc

    def _get_location(self, location: str, is_remote: bool) -> (int, str):
        if not location or is_remote:
            return "11047", "STATE"  # remote options
        url = f"{self.base_url}/findPopularLocationAjax.htm?maxLocationsToReturn=10&term={location}"
        session = create_session(self.proxy, has_retry=True)
        res = session.get(url)
        if res.status_code != 200:
            if res.status_code == 429:
                logger.error(f'429 Response - Blocked by Glassdoor for too many requests')
                return None, None
            else:
                logger.error(f'Glassdoor response status code {res.status_code}')
                return None, None
        items = res.json()

        if not items:
            raise ValueError(f"Location '{location}' not found on Glassdoor")
        location_type = items[0]["locationType"]
        if location_type == "C":
            location_type = "CITY"
        elif location_type == "S":
            location_type = "STATE"
        elif location_type == 'N':
            location_type = "COUNTRY"
        return int(items[0]["locationId"]), location_type

    def _add_payload(
        self,
        location_id: int,
        location_type: str,
        page_num: int,
        cursor: str | None = None,
    ) -> str:
        fromage = max(self.scraper_input.hours_old // 24, 1) if self.scraper_input.hours_old else None
        filter_params = []
        if self.scraper_input.easy_apply:
            filter_params.append({"filterKey": "applicationType", "values": "1"})
        if fromage:
            filter_params.append({"filterKey": "fromAge", "values": str(fromage)})
        payload = {
            "operationName": "JobSearchResultsQuery",
            "variables": {
                "excludeJobListingIds": [],
                "filterParams": filter_params,
                "keyword": self.scraper_input.search_term,
                "numJobsToShow": 30,
                "locationType": location_type,
                "locationId": int(location_id),
                "parameterUrlInput": f"IL.0,12_I{location_type}{location_id}",
                "pageNumber": page_num,
                "pageCursor": cursor,
                "fromage": fromage,
                "sort": "date"
            },
            "query": """
            query JobSearchResultsQuery(
                $excludeJobListingIds: [Long!], 
                $keyword: String, 
                $locationId: Int, 
                $locationType: LocationTypeEnum, 
                $numJobsToShow: Int!, 
                $pageCursor: String, 
                $pageNumber: Int, 
                $filterParams: [FilterParams], 
                $originalPageUrl: String, 
                $seoFriendlyUrlInput: String, 
                $parameterUrlInput: String, 
                $seoUrl: Boolean
            ) {
                jobListings(
                    contextHolder: {
                        searchParams: {
                            excludeJobListingIds: $excludeJobListingIds, 
                            keyword: $keyword, 
                            locationId: $locationId, 
                            locationType: $locationType, 
                            numPerPage: $numJobsToShow, 
                            pageCursor: $pageCursor, 
                            pageNumber: $pageNumber, 
                            filterParams: $filterParams, 
                            originalPageUrl: $originalPageUrl, 
                            seoFriendlyUrlInput: $seoFriendlyUrlInput, 
                            parameterUrlInput: $parameterUrlInput, 
                            seoUrl: $seoUrl, 
                            searchType: SR
                        }
                    }
                ) {
                    companyFilterOptions {
                        id
                        shortName
                        __typename
                    }
                    filterOptions
                    indeedCtk
                    jobListings {
                        ...JobView
                        __typename
                    }
                    jobListingSeoLinks {
                        linkItems {
                            position
                            url
                            __typename
                        }
                        __typename
                    }
                    jobSearchTrackingKey
                    jobsPageSeoData {
                        pageMetaDescription
                        pageTitle
                        __typename
                    }
                    paginationCursors {
                        cursor
                        pageNumber
                        __typename
                    }
                    indexablePageForSeo
                    searchResultsMetadata {
                        searchCriteria {
                            implicitLocation {
                                id
                                localizedDisplayName
                                type
                                __typename
                            }
                            keyword
                            location {
                                id
                                shortName
                                localizedShortName
                                localizedDisplayName
                                type
                                __typename
                            }
                            __typename
                        }
                        helpCenterDomain
                        helpCenterLocale
                        jobSerpJobOutlook {
                            occupation
                            paragraph
                            __typename
                        }
                        showMachineReadableJobs
                        __typename
                    }
                    totalJobsCount
                    __typename
                }
            }

            fragment JobView on JobListingSearchResult {
                jobview {
                    header {
                        adOrderId
                        advertiserType
                        adOrderSponsorshipLevel
                        ageInDays
                        divisionEmployerName
                        easyApply
                        employer {
                            id
                            name
                            shortName
                            __typename
                        }
                        employerNameFromSearch
                        goc
                        gocConfidence
                        gocId
                        jobCountryId
                        jobLink
                        jobResultTrackingKey
                        jobTitleText
                        locationName
                        locationType
                        locId
                        needsCommission
                        payCurrency
                        payPeriod
                        payPeriodAdjustedPay {
                            p10
                            p50
                            p90
                            __typename
                        }
                        rating
                        salarySource
                        savedJobId
                        sponsored
                        __typename
                    }
                    job {
                        description
                        importConfigId
                        jobTitleId
                        jobTitleText
                        listingId
                        __typename
                    }
                    jobListingAdminDetails {
                        cpcVal
                        importConfigId
                        jobListingId
                        jobSourceId
                        userEligibleForAdminJobDetails
                        __typename
                    }
                    overview {
                        shortName
                        squareLogoUrl
                        __typename
                    }
                    __typename
                }
                __typename
            }
            """
        }
        if self.scraper_input.job_type:
            payload["variables"]["filterParams"].append(
                {"filterKey": "jobType", "values": self.scraper_input.job_type.value[0]}
            )
        return json.dumps([payload])

    @staticmethod
    def parse_compensation(data: dict) -> Optional[Compensation]:
        pay_period = data.get("payPeriod")
        adjusted_pay = data.get("payPeriodAdjustedPay")
        currency = data.get("payCurrency", "USD")
        if not pay_period or not adjusted_pay:
            return None

        interval = None
        if pay_period == "ANNUAL":
            interval = CompensationInterval.YEARLY
        elif pay_period:
            interval = CompensationInterval.get_interval(pay_period)
        min_amount = int(adjusted_pay.get("p10") // 1)
        max_amount = int(adjusted_pay.get("p90") // 1)
        return Compensation(
            interval=interval,
            min_amount=min_amount,
            max_amount=max_amount,
            currency=currency,
        )

    @staticmethod
    def get_job_type_enum(job_type_str: str) -> list[JobType] | None:
        for job_type in JobType:
            if job_type_str in job_type.value:
                return [job_type]

    @staticmethod
    def parse_location(location_name: str) -> Location | None:
        if not location_name or location_name == "Remote":
            return
        city, _, state = location_name.partition(", ")
        return Location(city=city, state=state)

    @staticmethod
    def get_cursor_for_page(pagination_cursors, page_num):
        for cursor_data in pagination_cursors:
            if cursor_data["pageNumber"] == page_num:
                return cursor_data["cursor"]

    headers = {
        "authority": "www.glassdoor.com",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "apollographql-client-name": "job-search-next",
        "apollographql-client-version": "4.65.5",
        "content-type": "application/json",
        "gd-csrf-token": "Ft6oHEWlRZrxDww95Cpazw:0pGUrkb2y3TyOpAIqF2vbPmUXoXVkD3oEGDVkvfeCerceQ5-n8mBg3BovySUIjmCPHCaW0H2nQVdqzbtsYqf4Q:wcqRqeegRUa9MVLJGyujVXB7vWFPjdaS1CtrrzJq-ok",
        "origin": "https://www.glassdoor.com",
        "referer": "https://www.glassdoor.com/",
        "sec-ch-ua": '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    }
