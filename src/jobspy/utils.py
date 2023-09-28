import re
from typing import Optional


def extract_emails_from_text(text: str) -> Optional[list[str]]:
    if not text:
        return None
    email_regex = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
    return email_regex.findall(text)
