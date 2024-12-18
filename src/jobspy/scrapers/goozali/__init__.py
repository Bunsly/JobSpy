"""
jobspy.scrapers.Goozali
~~~~~~~~~~~~~~~~~~~

This module contains routines to scrape Goozali.
"""

from __future__ import annotations
import datetime
import json


from jobspy.scrapers import Scraper, ScraperInput
from jobspy.scrapers.goozali.GoozaliMapper import GoozaliMapper
from jobspy.scrapers.goozali.GoozaliScrapperComponent import GoozaliScrapperComponent
from jobspy.scrapers.goozali.model import GoozaliRow, GoozaliColumn, GoozaliResponse, GoozaliPartRequest, GoozaliFullRequest
from jobspy.scrapers.goozali.model.GoozaliColumnChoice import GoozaliColumnChoice
from jobspy.scrapers.site import Site

from ..utils import create_session, create_logger
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
        self.mapper = GoozaliMapper()
        self.base_url = "https://airtable.com/v0.3/view/{view_id}/readSharedViewData"
        self.view_ids = ["viwIOzPYaUGxlA0Jd"]
        self.component = GoozaliScrapperComponent()

    def scrape(self, scraper_input: ScraperInput) -> JobResponse:
        """
        Scrapes Goozali for jobs with scraper_input criteria
        :param scraper_input:
        :return: job_response
        """
        self.scraper_input = scraper_input
        job_list: list[JobPost] = []
        seen_ids = set()
        for view_id in self.view_ids:
            full_request = GoozaliFullRequest(self.base_url)
            part_request = GoozaliPartRequest(self.base_url)
            try:
                response = self.session.get(
                    url=full_request.url,
                    params=full_request.params,
                    timeout=10,
                    headers=full_request.headers,
                    cookies=full_request.cookies)
                logger.info(f"response: {str(response)}")
                if (response.status_code != 200):
                    logger.error(f"Status code: {response.status_code}, Error: {
                                 str(response.text)}")
                    return JobResponse(jobs=job_list)
            except Exception as e:
                logger.error(f"Exception: {str(e)}")
            # model the response with models
            goozali_response = self.mapper.map_response_to_goozali_response(
                response=response)
            # suggestL create groupby field and then filter by hours
            # filter result by Field
            column = self.component.find_column(
                goozali_response.data.columns, "Field")
            column_choice = self.component.find_choice_from_column(
                column, "Software Engineering")
            filtered_rows_by_column_choice = self.component.filter_rows_by_column_choice(
                goozali_response.data.rows, column, column_choice)
            filtered_rows_by_age_and_column_choice = self.component.filter_rows_by_hours(
                filtered_rows_by_column_choice, scraper_input.hours_old)
            # map to JobResponse Object

        return JobResponse(jobs=job_list)
