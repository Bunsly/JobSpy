import re

import requests
import tls_client
from ..jobs import JobType


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


def create_session(proxy: dict | None = None, is_tls: bool = True):
    """
    Creates a tls client session

    :return: A session object with or without proxies.
    """
    if is_tls:
        session = tls_client.Session(
            client_identifier="chrome112",
            random_tls_extension_order=True,
        )
        session.proxies = proxy
        # TODO multiple proxies
        # if self.proxies:
        #     session.proxies = {
        #         "http": random.choice(self.proxies),
        #         "https": random.choice(self.proxies),
        #     }
    else:
        session = requests.Session()
        session.allow_redirects = True
        if proxy:
            session.proxies.update(proxy)

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
