import re
import numpy as np

import tls_client
import requests
from requests.adapters import HTTPAdapter, Retry

from ..jobs import JobType


def modify_and_get_description(soup):
    for li in soup.find_all('li'):
        li.string = "- " + li.get_text()

    description = soup.get_text(separator='\n').strip()
    description = re.sub(r'\n+', '\n', description)
    return description


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
        session = tls_client.Session(
            client_identifier="chrome112",
            random_tls_extension_order=True,
        )
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
