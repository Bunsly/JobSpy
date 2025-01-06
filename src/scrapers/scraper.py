from abc import ABC, abstractmethod

from jobs import JobResponse
from scrapers.site import Site
from scrapers.scraper_input import ScraperInput


class Scraper(ABC):
    def __init__(
        self, site: Site, proxies: list[str] | None = None, ca_cert: str | None = None
    ):
        self.site = site
        self.proxies = proxies
        self.ca_cert = ca_cert

    @abstractmethod
    def scrape(self, scraper_input: ScraperInput) -> JobResponse: ...