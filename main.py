from jobspy import scrape_jobs
import pandas as pd

jobs: pd.DataFrame = scrape_jobs(
    site_name=["indeed", "linkedin", "zip_recruiter"],
    search_term="software engineer",
    results_wanted=10,

    # country: only needed for indeed
    country='hong kong'
)

if jobs.empty:
    print("No jobs found.")
else:
    #1 print
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 50)  # set to 0 to see full job url / desc
    print(jobs)

    #2 display in Jupyter Notebook
    #display(jobs)

    #3 output to .csv
    #jobs.to_csv('jobs.csv', index=False)