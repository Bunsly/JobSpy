"""
jobspy.scrapers.Goozali
~~~~~~~~~~~~~~~~~~~

This module contains routines to scrape Goozali.
"""

from __future__ import annotations

from jobspy.scrapers import Scraper, ScraperInput
from jobspy.scrapers.site import Site

from ..utils import create_session, create_logger
from .constants import get_access_policy, headers, cookies, stringifiedObjectParams, request_id, view_ids
from ...jobs import (
    JobPost,
    JobResponse,
)
logger = create_logger("Goozali")


class GoozaliScraper(Scraper):
    delay = 3
    band_delay = 4
    jobs_per_page = 25

    def __init__(
        self, proxies: list[str] | str | None = None, ca_cert: str | None = None
    ):
        """
        Initializes GoozaliScraper with the Goozalijob search url
        """
        super().__init__(site=Site.GOOZALI, proxies=proxies, ca_cert=ca_cert)
        self.session = create_session(
            proxies=self.proxies,
            ca_cert=ca_cert,
            is_tls=False,
            has_retry=True,
            delay=5,
            clear_cookies=False,
        )
        self.base_url = "https://airtable.com/v0.3/view/{view_id}/readSharedViewData"

    def _get_params(self, view_id: str) -> dict[str, str]:
        access_policy = get_access_policy(view_id)
        params = {
            "stringifiedObjectParams": stringifiedObjectParams,
            "request_id": request_id,
            "accessPolicy": access_policy
        }

        return {k: v for k, v in params.items() if v is not None}

    def scrape(self, scraper_input: ScraperInput) -> JobResponse:
        """
        Scrapes Goozali for jobs with scraper_input criteria
        :param scraper_input:
        :return: job_response
        """
        self.scraper_input = scraper_input
        job_list: list[JobPost] = []
        seen_ids = set()
        for view_id in view_ids:
            # create url
            url = self.base_url.format(view_id=view_id)
            params = self._get_params(view_id)
            # create session -> run the api
            try:
                response = self.session.get(
                    url=url,
                    params=params,
                    timeout=10,
                    headers=headers,
                    cookies=cookies
                )
                logger.info(f"response: {str(response)}")
                if (response.status_code != 200):
                    logger.error(f"Status code: {
                                 response.status_code}, Error: {str(response.text)}")
                    return JobResponse(jobs=job_list)
            except Exception as e:
                logger.error(f"Exception: {str(e)}")
            # model the response with models
            # create map columnId to Column object
            # filter result by Field like the web
            # filter by date
            # map to JobResponse Object
        return JobResponse(jobs=job_list)
