from ..jobspy import scrape_jobs
import pandas as pd


def test_indeed():
    result = scrape_jobs(
        site_name="glassdoor", search_term="software engineer", country_indeed="USA"
    )
    assert (
        isinstance(result, pd.DataFrame) and not result.empty
    ), "Result should be a non-empty DataFrame"
