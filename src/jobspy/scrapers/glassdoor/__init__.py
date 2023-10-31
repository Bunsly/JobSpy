"""
jobspy.scrapers.glassdoor
~~~~~~~~~~~~~~~~~~~

This module contains routines to scrape Glassdoor.
"""
import math
import time
import re
import json
from datetime import datetime, date
from typing import Optional, Tuple, Any
from bs4 import BeautifulSoup

from .. import Scraper, ScraperInput, Site
from ..exceptions import GlassdoorException
from ..utils import count_urgent_words, extract_emails_from_text, create_session
from ...jobs import (
    JobPost,
    Compensation,
    CompensationInterval,
    Location,
    JobResponse,
    JobType,
    Country,
)


class GlassdoorScraper(Scraper):
    def __init__(self, proxy: Optional[str] = None):
        """
        Initializes GlassdoorScraper with the Glassdoor job search url
        """
        site = Site(Site.ZIP_RECRUITER)
        super().__init__(site, proxy=proxy)

        self.url = None
        self.country = None
        self.jobs_per_page = 30
        self.seen_urls = set()

    def fetch_jobs_page(
        self,
        scraper_input: ScraperInput,
        location_id: int,
        location_type: str,
        page_num: int,
        cursor: str | None,
    ) -> (list[JobPost], str | None):
        """
        Scrapes a page of Glassdoor for jobs with scraper_input criteria
        :param scraper_input:
        :return: jobs found on page
        :return: cursor for next page
        """
        try:
            payload = self.add_payload(
                scraper_input, location_id, location_type, page_num, cursor
            )
            session = create_session(self.proxy, is_tls=False)
            response = session.post(
                f"{self.url}/graph", headers=self.headers(), timeout=10, data=payload
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
        for i, job in enumerate(jobs_data):
            job_url = res_json["data"]["jobListings"]["jobListingSeoLinks"][
                "linkItems"
            ][i]["url"]
            if job_url in self.seen_urls:
                continue
            self.seen_urls.add(job_url)
            job = job["jobview"]
            title = job["job"]["jobTitleText"]
            company_name = job["header"]["employerNameFromSearch"]
            location_name = job["header"].get("locationName", "")
            location_type = job["header"].get("locationType", "")
            is_remote = False
            location = None

            if location_type == "S":
                is_remote = True
            else:
                location = self.parse_location(location_name)

            compensation = self.parse_compensation(job["header"])

            job = JobPost(
                title=title,
                company_name=company_name,
                job_url=job_url,
                location=location,
                compensation=compensation,
                is_remote=is_remote,
            )
            jobs.append(job)

        return jobs, self.get_cursor_for_page(
            res_json["data"]["jobListings"]["paginationCursors"], page_num + 1
        )

    def scrape(self, scraper_input: ScraperInput) -> JobResponse:
        """
        Scrapes Glassdoor for jobs with scraper_input criteria.
        :param scraper_input: Information about job search criteria.
        :return: JobResponse containing a list of jobs.
        """
        self.country = scraper_input.country
        self.url = self.country.get_url()

        location_id, location_type = self.get_location(
            scraper_input.location, scraper_input.is_remote
        )
        all_jobs: list[JobPost] = []
        cursor = None
        max_pages = 30

        try:
            for page in range(
                1 + (scraper_input.offset // self.jobs_per_page),
                min(
                    (scraper_input.results_wanted // self.jobs_per_page) + 2,
                    max_pages + 1,
                ),
            ):
                try:
                    jobs, cursor = self.fetch_jobs_page(
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
        elif pay_period == "MONTHLY":
            interval = CompensationInterval.MONTHLY
        elif pay_period == "WEEKLY":
            interval = CompensationInterval.WEEKLY
        elif pay_period == "DAILY":
            interval = CompensationInterval.DAILY
        elif pay_period == "HOURLY":
            interval = CompensationInterval.HOURLY

        min_amount = int(adjusted_pay.get("p10") // 1)
        max_amount = int(adjusted_pay.get("p90") // 1)

        return Compensation(
            interval=interval,
            min_amount=min_amount,
            max_amount=max_amount,
            currency=currency,
        )

    def get_job_type_enum(self, job_type_str: str) -> list[JobType] | None:
        for job_type in JobType:
            if job_type_str in job_type.value:
                return [job_type]
        return None

    def get_location(self, location: str, is_remote: bool) -> (int, str):
        if not location or is_remote:
            return "11047", "STATE"  # remote options
        url = f"{self.url}/findPopularLocationAjax.htm?maxLocationsToReturn=10&term={location}"
        session = create_session(self.proxy)
        response = session.get(url)
        if response.status_code != 200:
            raise GlassdoorException(
                f"bad response status code: {response.status_code}"
            )
        items = response.json()
        if not items:
            raise ValueError(f"Location '{location}' not found on Glassdoor")
        location_type = items[0]["locationType"]
        if location_type == "C":
            location_type = "CITY"
        elif location_type == "S":
            location_type = "STATE"
        return int(items[0]["locationId"]), location_type

    @staticmethod
    def add_payload(
        scraper_input,
        location_id: int,
        location_type: str,
        page_num: int,
        cursor: str | None = None,
    ) -> dict[str, str | Any]:
        payload = {
            "operationName": "JobSearchResultsQuery",
            "variables": {
                "excludeJobListingIds": [],
                "filterParams": [],
                "keyword": scraper_input.search_term,
                "numJobsToShow": 30,
                "locationType": location_type,
                "locationId": int(location_id),
                "parameterUrlInput": f"IL.0,12_I{location_type}{location_id}",
                "pageNumber": page_num,
                "pageCursor": cursor,
            },
            "query": "query JobSearchResultsQuery($excludeJobListingIds: [Long!], $keyword: String, $locationId: Int, $locationType: LocationTypeEnum, $numJobsToShow: Int!, $pageCursor: String, $pageNumber: Int, $filterParams: [FilterParams], $originalPageUrl: String, $seoFriendlyUrlInput: String, $parameterUrlInput: String, $seoUrl: Boolean) {\n  jobListings(\n    contextHolder: {searchParams: {excludeJobListingIds: $excludeJobListingIds, keyword: $keyword, locationId: $locationId, locationType: $locationType, numPerPage: $numJobsToShow, pageCursor: $pageCursor, pageNumber: $pageNumber, filterParams: $filterParams, originalPageUrl: $originalPageUrl, seoFriendlyUrlInput: $seoFriendlyUrlInput, parameterUrlInput: $parameterUrlInput, seoUrl: $seoUrl, searchType: SR}}\n  ) {\n    companyFilterOptions {\n      id\n      shortName\n      __typename\n    }\n    filterOptions\n    indeedCtk\n    jobListings {\n      ...JobView\n      __typename\n    }\n    jobListingSeoLinks {\n      linkItems {\n        position\n        url\n        __typename\n      }\n      __typename\n    }\n    jobSearchTrackingKey\n    jobsPageSeoData {\n      pageMetaDescription\n      pageTitle\n      __typename\n    }\n    paginationCursors {\n      cursor\n      pageNumber\n      __typename\n    }\n    indexablePageForSeo\n    searchResultsMetadata {\n      searchCriteria {\n        implicitLocation {\n          id\n          localizedDisplayName\n          type\n          __typename\n        }\n        keyword\n        location {\n          id\n          shortName\n          localizedShortName\n          localizedDisplayName\n          type\n          __typename\n        }\n        __typename\n      }\n      footerVO {\n        countryMenu {\n          childNavigationLinks {\n            id\n            link\n            textKey\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      helpCenterDomain\n      helpCenterLocale\n      jobAlert {\n        jobAlertExists\n        __typename\n      }\n      jobSerpFaq {\n        questions {\n          answer\n          question\n          __typename\n        }\n        __typename\n      }\n      jobSerpJobOutlook {\n        occupation\n        paragraph\n        __typename\n      }\n      showMachineReadableJobs\n      __typename\n    }\n    serpSeoLinksVO {\n      relatedJobTitlesResults\n      searchedJobTitle\n      searchedKeyword\n      searchedLocationIdAsString\n      searchedLocationSeoName\n      searchedLocationType\n      topCityIdsToNameResults {\n        key\n        value\n        __typename\n      }\n      topEmployerIdsToNameResults {\n        key\n        value\n        __typename\n      }\n      topEmployerNameResults\n      topOccupationResults\n      __typename\n    }\n    totalJobsCount\n    __typename\n  }\n}\n\nfragment JobView on JobListingSearchResult {\n  jobview {\n    header {\n      adOrderId\n      advertiserType\n      adOrderSponsorshipLevel\n      ageInDays\n      divisionEmployerName\n      easyApply\n      employer {\n        id\n        name\n        shortName\n        __typename\n      }\n      employerNameFromSearch\n      goc\n      gocConfidence\n      gocId\n      jobCountryId\n      jobLink\n      jobResultTrackingKey\n      jobTitleText\n      locationName\n      locationType\n      locId\n      needsCommission\n      payCurrency\n      payPeriod\n      payPeriodAdjustedPay {\n        p10\n        p50\n        p90\n        __typename\n      }\n      rating\n      salarySource\n      savedJobId\n      sponsored\n      __typename\n    }\n    job {\n      descriptionFragments\n      importConfigId\n      jobTitleId\n      jobTitleText\n      listingId\n      __typename\n    }\n    jobListingAdminDetails {\n      cpcVal\n      importConfigId\n      jobListingId\n      jobSourceId\n      userEligibleForAdminJobDetails\n      __typename\n    }\n    overview {\n      shortName\n      squareLogoUrl\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n",
        }

        job_type_filters = {
            JobType.FULL_TIME: "fulltime",
            JobType.PART_TIME: "parttime",
            JobType.CONTRACT: "contract",
            JobType.INTERNSHIP: "internship",
            JobType.TEMPORARY: "temporary",
        }

        if scraper_input.job_type in job_type_filters:
            filter_value = job_type_filters[scraper_input.job_type]
            payload["variables"]["filterParams"].append(
                {"filterKey": "jobType", "values": filter_value}
            )

        return json.dumps([payload])

    def parse_location(self, location_name: str) -> Location:
        if not location_name or location_name == "Remote":
            return None
        city, _, state = location_name.partition(", ")
        return Location(city=city, state=state)

    @staticmethod
    def get_cursor_for_page(pagination_cursors, page_num):
        for cursor_data in pagination_cursors:
            if cursor_data["pageNumber"] == page_num:
                return cursor_data["cursor"]
        return None

    @staticmethod
    def headers() -> dict:
        """
        Returns headers needed for requests
        :return: dict - Dictionary containing headers
        """
        return {
            "authority": "www.glassdoor.com",
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "apollographql-client-name": "job-search-next",
            "apollographql-client-version": "4.65.5",
            "content-type": "application/json",
            "cookie": 'gdId=91e2dfc4-c8b5-4fa7-83d0-11512b80262c; G_ENABLED_IDPS=google; trs=https%3A%2F%2Fwww.redhat.com%2F:referral:referral:2023-07-05+09%3A50%3A14.862:undefined:undefined; g_state={"i_p":1688587331651,"i_l":1}; _cfuvid=.7llazxhYFZWi6EISSPdVjtqF0NMVwzxr_E.cB1jgLs-1697828392979-0-604800000; GSESSIONID=undefined; JSESSIONID=F03DD1B5EE02DB6D842FE42B142F88F3; cass=1; jobsClicked=true; indeedCtk=1hd77b301k79i801; asst=1697829114.2; G_AUTHUSER_H=0; uc=8013A8318C98C517FE6DD0024636DFDEF978FC33266D93A2FAFEF364EACA608949D8B8FA2DC243D62DE271D733EB189D809ABE5B08D7B1AE865D217BD4EEBB97C282F5DA5FEFE79C937E3F6110B2A3A0ADBBA3B4B6DF5A996FEE00516100A65FCB11DA26817BE8D1C1BF6CFE36B5B68A3FDC2CFEC83AB797F7841FBB157C202332FC7E077B56BD39B167BDF3D9866E3B; AWSALB=zxc/Yk1nbWXXT6HjNyn3H4h4950ckVsFV/zOrq5LSoChYLE1qV+hDI8Axi3fUa9rlskndcO0M+Fw+ZnJ+AQ2afBFpyOd1acouLMYgkbEpqpQaWhY6/Gv4QH1zBcJ; AWSALBCORS=zxc/Yk1nbWXXT6HjNyn3H4h4950ckVsFV/zOrq5LSoChYLE1qV+hDI8Axi3fUa9rlskndcO0M+Fw+ZnJ+AQ2afBFpyOd1acouLMYgkbEpqpQaWhY6/Gv4QH1zBcJ; gdsid=1697828393025:1697830776351:668396EDB9E6A832022D34414128093D; at=HkH8Hnqi9uaMC7eu0okqyIwqp07ht9hBvE1_St7E_hRqPvkO9pUeJ1Jcpds4F3g6LL5ADaCNlxrPn0o6DumGMfog8qI1-zxaV_jpiFs3pugntw6WpVyYWdfioIZ1IDKupyteeLQEM1AO4zhGjY_rPZynpsiZBPO_B1au94sKv64rv23yvP56OiWKKfI-8_9hhLACEwWvM-Az7X-4aE2QdFt93VJbXbbGVf07bdDZfimsIkTtgJCLSRhU1V0kEM1Efyu66vo3m77gFFaMW7lxyYnb36I5PdDtEXBm3aL-zR7-qa5ywd94ISEivgqQOA4FPItNhqIlX4XrfD1lxVz6rfPaoTIDi4DI6UMCUjwyPsuv8mn0rYqDfRnmJpZ97fJ5AnhrknAd_6ZWN5v1OrxJczHzcXd8LO820QPoqxzzG13bmSTXLwGSxMUCtSrVsq05hicimQ3jpRt0c1dA4OkTNqF7_770B9JfcHcM8cr8-C4IL56dnOjr9KBGfN1Q2IvZM2cOBRbV7okiNOzKVZ3qJ24AE34WA2F3U6Whiu6H8nIuGG5hSNkVygY6CtglNZfFF9p8pJAZm79PngrrBv-CXFBZmhYLFo46lmFetDkiJ6mirtez4tKpzTIYjIp4_JAkiZFwbLJ2QGH4mK8kyyW0lZiX1DTuQec50N_5wvRo0Gt7nlKxzLsApMnaNhuQeH5ygh_pa381ORo9mQGi0EYF9zk00pa2--z4PtjfQ8KFq36GgpxKy5-o4qgqygZj8F01L8r-FiX2G4C7PREMIpAyHX2A4-_JxA1IS2j12EyqKTLqE9VcP06qm2Z-YuIW3ctmpMxy5G9_KiEiGv17weizhSFnl6SbpAEY-2VSmQ5V6jm3hoMp2jemkuGCRkZeFstLDEPxlzFN7WM; __cf_bm=zGaVjIJw4irf40_7UVw54B6Ohm271RUX4Tc8KVScrbs-1697830777-0-AYv2GnKTnnCU+cY9xHbJunO0DwlLDO6SIBnC/s/qldpKsGK0rRAjD6y8lbyATT/KlS7g29OZaN4fbd0lrJg0KmWbIybZIzfWVLHSYePVuOhu; asst=1697829114.2; at=dFhXf64wsf2TlnWy41xLs7skJkuxgKToEGcjGtDfUvW4oEAJ4tTIR5dKQ8wbwT75aIaGgdCfvcb-da7vwrCGWscCncmfLFQpJ9l-LLwoRfk-pMsxHhd77wvf-W7I0HSm7-Q5lQJqI9WyNGRxOa-RpzBTf4L8_Et4-3FzjPaAoYY5pY1FhuwXbN5asGOAMW-p8cjpbfn3PumlIYuckguWnjrcY2F31YJ_1noeoHM9tCGpymANbqGXRkG6aXY7yCfVXtdgZU1K5SMeaSPZIuF_iLUxjc_corzpNiH6qq7BIAmh-e5Aa-g7cwpZcln1fmwTVw4uTMZf1eLIMTa9WzgqZNkvG-sGaq_XxKA_Wai6xTTkOHfRgm4632Ba2963wdJvkGmUUa3tb_L4_wTgk3eFnHp5JhghLfT2Pe3KidP-yX__vx8JOsqe3fndCkKXgVz7xQKe1Dur-sMNlGwi4LXfguTT2YUI8C5Miq3pj2IHc7dC97eyyAiAM4HvyGWfaXWZcei6oIGrOwMvYgy0AcwFry6SIP2SxLT5TrxinRRuem1r1IcOTJsMJyUPp1QsZ7bOyq9G_0060B4CPyovw5523hEuqLTM-R5e5yavY6C_1DHUyE15C3mrh7kdvmlGZeflnHqkFTEKwwOftm-Mv-CKD5Db9ABFGNxKB2FH7nDH67hfOvm4tGNMzceBPKYJ3wciTt9jK3wy39_7cOYVywfrZ-oLhw_XtsbGSSeGn3HytrfgSADAh2sT0Gg6eCC9Xy1vh-Za337SVLUDXZ73W2xJxxUHBkFzZs8L_Xndo5DsbpWhVs9IYUGyraJdqB3SLgDbAppIBCJl4fx6_DG8-xOQPBvuFMlTROe1JVdHOzXI1GElwFDTuH1pjkg4I2G0NhAbE06Y-1illQE; gdsid=1697828393025:1697831731408:99C30D94108AC3030D61C736DDCDF11C',
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
