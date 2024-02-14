import re
import logging
import numpy as np

import html2text
import tls_client
import requests
from requests.adapters import HTTPAdapter, Retry

from ..jobs import JobType

text_maker = html2text.HTML2Text()
logger = logging.getLogger("JobSpy")
logger.propagate = False
if not logger.handlers:
    logger.setLevel(logging.ERROR)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


def count_urgent_words(description: str) -> int:
    """
    Count the number of urgent words or phrases in a job description.
    """
    urgent_patterns = re.compile(
        r"\burgen(t|cy)|\bimmediate(ly)?\b|start asap|\bhiring (now|immediate(ly)?)\b",
        re.IGNORECASE,
    )
    matches = re.findall(urgent_patterns, description)
    count = len(matches)

    return count


def markdown_converter(description_html: str):
    if description_html is None:
        return ""
    text_maker.ignore_links = False
    try:
        markdown = text_maker.handle(description_html)
        return markdown.strip()
    except AssertionError as e:
        return ""


def extract_emails_from_text(text: str) -> list[str] | None:
    if not text:
        return None
    email_regex = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
    return email_regex.findall(text)


def create_session(proxy: dict | None = None, is_tls: bool = True, has_retry: bool = False, delay: int = 1) -> requests.Session:
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
            retries = Retry(total=3,
                            connect=3,
                            status=3,
                            status_forcelist=[500, 502, 503, 504, 429],
                            backoff_factor=delay)
            adapter = HTTPAdapter(max_retries=retries)

            session.mount('http://', adapter)
            session.mount('https://', adapter)
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
    cur_str = re.sub("[^-0-9.,]", '', cur_str)
    # Remove any 000s separators (either , or .)
    cur_str = re.sub("[.,]", '', cur_str[:-3]) + cur_str[-3:]

    if '.' in list(cur_str[-3:]):
        num = float(cur_str)
    elif ',' in list(cur_str[-3:]):
        num = float(cur_str.replace(',', '.'))
    else:
        num = float(cur_str)

    return np.round(num, 2)


