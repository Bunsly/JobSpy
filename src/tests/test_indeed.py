from ..jobspy import scrape_jobs
import pandas as pd


def test_indeed():
    result = scrape_jobs(
        site_name="indeed",
        search_term="software engineer",
        country_indeed="usa",
        results_wanted=5,
    )
    assert (
        isinstance(result, pd.DataFrame) and not result.empty
    ), "Result should be a non-empty DataFrame"
