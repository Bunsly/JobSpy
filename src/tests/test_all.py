from ..jobspy import scrape_jobs
import pandas as pd


def test_all():
    result = scrape_jobs(
        site_name=[
            "linkedin",
            "indeed",
            "glassdoor",
        ],  # ziprecruiter needs good ip, and temp fix to pass test on ci
        search_term="engineer",
        results_wanted=5,
    )

    assert (
        isinstance(result, pd.DataFrame) and len(result) == 15
    ), "Result should be a non-empty DataFrame"
