import csv

from jobspy import scrape_jobs 

jobs = scrape_jobs(
    # site_name=["indeed", "linkedin", "zip_recruiter", "glassdoor", "google"],
    site_name=["glassdoor"],
    search_term="software engineer",
    google_search_term="software engineer jobs near Tel Aviv Israel since yesterday",
    location="Tel Aviv, israel",
    results_wanted=20,
    hours_old=72,
    country_indeed='israel',
    
    # linkedin_fetch_description=True # gets more info such as description, direct job url (slower)
    # proxies=["208.195.175.46:65095", "208.195.175.45:65095", "localhost"],
)
print(f"Found {len(jobs)} jobs")
print(jobs.head())
jobs.to_csv("jobs.csv", quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False) # to_excel