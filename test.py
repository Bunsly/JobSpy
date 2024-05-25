import csv
from src.jobspy import scrape_jobs

proxies = [
    "http://xvwnpgzc:8516e8nu5s24@38.154.227.167:5868",
    "http://xvwnpgzc:8516e8nu5s24@185.199.229.156:7492",
    "http://xvwnpgzc:8516e8nu5s24@185.199.228.220:7300",
    "http://xvwnpgzc:8516e8nu5s24@185.199.231.45:8382",
    "http://xvwnpgzc:8516e8nu5s24@188.74.210.207:6286",
    "http://xvwnpgzc:8516e8nu5s24@188.74.183.10:8279",
    "http://xvwnpgzc:8516e8nu5s24@188.74.210.21:6100",
    "http://xvwnpgzc:8516e8nu5s24@45.155.68.129:8133",
    "http://xvwnpgzc:8516e8nu5s24@154.95.36.199:6893",
    "http://xvwnpgzc:8516e8nu5s24@45.94.47.66:8110",
]


jobs = scrape_jobs(
    site_name=["indeed", "linkedin", "zip_recruiter", "glassdoor"],
    search_term="software engineer",
    results_wanted=500,
    hours_old=72,  # (only Linkedin/Indeed is hour specific, others round up to days old)
    country_indeed="usa",
    # linkedin_fetch_description=True,
    proxy=proxies,
)
jobs.to_csv("jobs.csv", quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)
