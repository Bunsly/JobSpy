from __future__ import annotations

import logging
import re
import time
from datetime import date, datetime, timezone
from itertools import cycle
from typing import Any, TypeVar

import requests
from bs4 import BeautifulSoup
from curl_cffi import CurlOpt
from curl_cffi import requests as curl_requests
from markdownify import markdownify as md

from jobspy.model import (
    DescriptionFormat,
    JobType,
    ScraperInput,
)

log_handler = logging.StreamHandler()
log_handler.setFormatter(logging.Formatter(logging.BASIC_FORMAT))


def configure_logging(verbose: int | None) -> None:
    """verbose: 0 errors only, 1 adds warnings, 2 all logs, None leaves the level alone"""
    logger = logging.getLogger("jobspy")
    if logging.root.handlers or any(h is not log_handler for h in logger.handlers):
        logger.removeHandler(log_handler)
    else:
        logger.addHandler(log_handler)
    if verbose is not None:
        logger.setLevel([logging.ERROR, logging.WARNING, logging.INFO][verbose])


class RotatingProxySession:
    request_timeout = 15
    verify: bool | str

    def __init__(self, proxies: list[str] | None = None) -> None:
        proxies = proxies or []
        self.rotates = len(set(proxies)) > 1
        self.proxy_cycle = cycle(map(self.format_proxy, proxies)) if proxies else None

    @staticmethod
    def format_proxy(proxy: str) -> dict[str, str]:
        """Utility method to format a proxy string into a dictionary."""
        if proxy in ("localhost", "http://localhost"):
            proxy = ""
        elif not re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*://", proxy):
            proxy = f"http://{proxy}"
        return {"http": proxy, "https": proxy}

    def request(self, *args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
        if self.proxy_cycle:
            kwargs["proxies"] = next(self.proxy_cycle)
        kwargs.setdefault("verify", self.verify)
        kwargs.setdefault("timeout", self.request_timeout)
        return super().request(*args, **kwargs)  # type: ignore[misc]


class RequestsRotating(RotatingProxySession, requests.Session):
    def __init__(
        self, proxies: list[str] | None = None, clear_cookies: bool = False
    ) -> None:
        RotatingProxySession.__init__(self, proxies=proxies)
        requests.Session.__init__(self)
        self.clear_cookies = clear_cookies

    def request(self, *args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
        if self.clear_cookies:
            self.cookies.clear()
        return super().request(*args, **kwargs)


class TLSRotating(  # type: ignore[misc]
    RotatingProxySession, curl_requests.Session[curl_requests.Response]
):
    def __init__(self, proxies: list[str] | None = None) -> None:
        RotatingProxySession.__init__(self, proxies=proxies)
        curl_requests.Session.__init__(
            self,
            impersonate="chrome",
            allow_redirects=False,
            curl_options={CurlOpt.SSL_SESSIONID_CACHE: 0} if self.rotates else None,
        )


S = TypeVar("S", RequestsRotating, TLSRotating)


def create_session(
    session: S, scraper_input: ScraperInput, headers: dict[str, str] | None = None
) -> S:
    if scraper_input.ca_cert:
        session.verify = str(scraper_input.ca_cert)
    if headers:
        session.headers.update(headers)
    if scraper_input.user_agent:
        session.headers["user-agent"] = scraper_input.user_agent
    return session


def check_status(response: requests.Response | curl_requests.Response) -> None:
    if response.status_code != 200:
        hint = " (blocked: use a proxy)" if response.status_code in (403, 429) else ""
        raise ValueError(f"response status code {response.status_code}{hint}")


def _as_markup(text: str) -> str:
    return text if "<" in text else f"<!---->{text}"


def plain_converter(description_html: str | None) -> str | None:
    if description_html is None:
        return None
    soup = BeautifulSoup(_as_markup(description_html), "html.parser")
    return re.sub(r"\s+", " ", soup.get_text(separator=" ")).strip()


def extract_emails_from_text(text: str | None) -> list[str] | None:
    if not text:
        return None
    email_regex = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
    return list(dict.fromkeys(email_regex.findall(text)))


def description_fields(
    html: str | None, description_format: DescriptionFormat
) -> dict[str, object]:
    """The description in the format asked for, and the emails in it."""
    if html is None:
        return {"description": None, "emails": None}
    description: str | None
    if description_format == DescriptionFormat.MARKDOWN:
        description = md(_as_markup(html)).strip()
    elif description_format == DescriptionFormat.PLAIN:
        description = plain_converter(html)
    else:
        description = html
    return {
        "description": description or None,
        "emails": extract_emails_from_text(html),
    }


def utc_date(epoch: float | None) -> date | None:
    """The UTC date of a Unix time in seconds; None for a missing or zero one."""
    return datetime.fromtimestamp(epoch, timezone.utc).date() if epoch else None


def too_old(posted: float, hours_old: int | None) -> bool:
    return bool(hours_old and posted and posted < time.time() - hours_old * 3600)


def get_enum_from_job_type(job_type_str: str) -> JobType | None:
    try:
        return JobType(job_type_str)
    except ValueError:
        return None
