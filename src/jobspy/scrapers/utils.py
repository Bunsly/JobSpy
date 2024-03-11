from __future__ import annotations

import re
import logging
import requests
import tls_client
import numpy as np
from markdownify import markdownify as md
from requests.adapters import HTTPAdapter, Retry

from ..jobs import JobType

logger = logging.getLogger("JobSpy")
logger.propagate = False
if not logger.handlers:
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(format)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


def set_logger_level(verbose: int = 2):
    """
    Adjusts the logger's level. This function allows the logging level to be changed at runtime.

    Parameters:
    - verbose: int {0, 1, 2} (default=2, all logs)
    """
    if verbose is None:
        return
    level_name = {2: "INFO", 1: "WARNING", 0: "ERROR"}.get(verbose, "INFO")
    level = getattr(logging, level_name.upper(), None)
    if level is not None:
        logger.setLevel(level)
    else:
        raise ValueError(f"Invalid log level: {level_name}")


def markdown_converter(description_html: str):
    if description_html is None:
        return None
    markdown = md(description_html)
    return markdown.strip()


def extract_emails_from_text(text: str) -> list[str] | None:
    if not text:
        return None
    email_regex = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
    return email_regex.findall(text)


def create_session(
    proxy: dict | None = None,
    is_tls: bool = True,
    has_retry: bool = False,
    delay: int = 1,
) -> requests.Session:
    """
    Creates a requests session with optional tls, proxy, and retry settings.
    :return: A session object
    """
    if is_tls:
        session = tls_client.Session(random_tls_extension_order=True)
        session.proxies = proxy
    else:
        session = requests.Session()
        session.allow_redirects = True
        if proxy:
            session.proxies.update(proxy)
        if has_retry:
            retries = Retry(
                total=3,
                connect=3,
                status=3,
                status_forcelist=[500, 502, 503, 504, 429],
                backoff_factor=delay,
            )
            adapter = HTTPAdapter(max_retries=retries)

            session.mount("http://", adapter)
            session.mount("https://", adapter)
    return session


def get_enum_from_job_type(job_type_str: str) -> JobType | None:
    """
    Given a string, returns the corresponding JobType enum member if a match is found.
    """
    res = None
    for job_type in JobType:
        if job_type_str in job_type.value:
            res = job_type
    return res


def currency_parser(cur_str):
    # Remove any non-numerical characters
    # except for ',' '.' or '-' (e.g. EUR)
    cur_str = re.sub("[^-0-9.,]", "", cur_str)
    # Remove any 000s separators (either , or .)
    cur_str = re.sub("[.,]", "", cur_str[:-3]) + cur_str[-3:]

    if "." in list(cur_str[-3:]):
        num = float(cur_str)
    elif "," in list(cur_str[-3:]):
        num = float(cur_str.replace(",", "."))
    else:
        num = float(cur_str)

    return np.round(num, 2)
