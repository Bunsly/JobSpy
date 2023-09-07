"""
jobspy.scrapers.exceptions
~~~~~~~~~~~~~~~~~~~

This module contains the set of Scrapers' exceptions.
"""


class LinkedInException(Exception):
    """Failed to scrape LinkedIn"""


class IndeedException(Exception):
    """Failed to scrape Indeed"""


class ZipRecruiterException(Exception):
    """Failed to scrape ZipRecruiter"""
