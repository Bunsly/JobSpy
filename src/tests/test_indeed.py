from ..jobspy import scrape_jobs
import pandas as pd


def test_indeed():
    result = scrape_jobs(
        site_name="indeed",
        search_term="software engineer",
    )
    assert isinstance(result, pd.DataFrame) and not result.empty, "Result should be a non-empty DataFrame"
