from jobspy import scrape_jobs


def test_linkedin():
    result = scrape_jobs(
        site_name="linkedin",
        search_term="software engineer",
    )
    assert result is not None
