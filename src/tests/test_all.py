from ..jobspy import scrape_jobs


def test_all():
    result = scrape_jobs(
        site_name=["linkedin", "indeed", "zip_recruiter"],
        search_term="software engineer",
        results_wanted=5,
    )
    assert result is not None and result.errors.empty is True
