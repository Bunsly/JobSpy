from jobscrape import scrape_jobs


def test_indeed():
    result = scrape_jobs(
        site_name="indeed",
        search_term="software engineer",
    )

    assert result is not None
