import re
import tls_client


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


def create_session(proxy: str | None = None):
    """
    Creates a tls client session

    :return: A session object with or without proxies.
    """
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

    return session
