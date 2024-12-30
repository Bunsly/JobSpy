from jobspy import scrape_jobs
import pandas as pd


def test_all():
    sites = [
        "indeed",
        "glassdoor",
    ]  # ziprecruiter/linkedin needs good ip, and temp fix to pass test on ci
    result = scrape_jobs(
        site_name=sites,
        search_term="engineer",
        results_wanted=5,
    )

    assert (
        isinstance(result, pd.DataFrame) and len(result) == len(sites) * 5
    ), "Result should be a non-empty DataFrame"
