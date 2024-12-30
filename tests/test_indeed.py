from jobspy import scrape_jobs
import pandas as pd


def test_indeed():
    result = scrape_jobs(
        site_name="indeed",
        search_term="engineer",
        results_wanted=5,
    )
    assert (
        isinstance(result, pd.DataFrame) and len(result) == 5
    ), "Result should be a non-empty DataFrame"
