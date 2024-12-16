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
from jobspy.scrapers.goozali.model import GoozaliRow, GoozaliColumn, GoozaliResponse, GoozaliPartRequest, GoozaliFullRequest
from jobspy.scrapers.site import Site

from ..utils import create_session, create_logger
from .constants import headers
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

    def map_respone_to_goozali_response(self, response) -> GoozaliResponse:
        # Check the response content (this is a bytes object)
        response_content = response.content
        # Decode the byte content to a string
        decoded_content = response_content.decode('utf-8')
        # Now you can parse the decoded content as JSON
        data = json.loads(decoded_content)

        return GoozaliResponse(**data)

    # Function to filter GoozaliRows based on hours old
    def filter_rows_by_hours(self, rows: list[GoozaliRow], hours: int) -> list[GoozaliRow]:
        # Current time
        now = datetime.datetime.now()

        # Calculate the time delta for the given hours
        time_delta = datetime.timedelta(hours=hours)

        # Filter rows
        filtered_rows = [
            row for row in rows
            if now - row.createdTime <= time_delta
        ]

        return filtered_rows

    def find_column(self, columns: list[GoozaliColumn], column_name: str) -> GoozaliColumn:
        for column in columns:
            if (column.name == column_name):
                return column

    # def filter_rows_by_column(rows: list[GoozaliRow], goozali_column: GoozaliColumn) -> list[GoozaliRow]:

    #     # Filter rows
    #     filtered_rows = [
    #         row for row in rows
    #         if row.cellValuesByColumnId[goozali_column.id] == goozali_column.
    #     ]

    #     return filtered_rows

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
            # filter by date
            filtered_rows_by_age = self.filter_rows_by_hours(
                goozali_response.data.rows, scraper_input.hours_old)
            # filter result by Field like the web
            field_cloumn = self.find_column(
                goozali_response.data.columns, "Field")
            # map to JobResponse Object

        return JobResponse(jobs=job_list)
