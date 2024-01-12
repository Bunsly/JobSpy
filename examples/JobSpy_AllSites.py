from jobspy import scrape_jobs
import pandas as pd

jobs: pd.DataFrame = scrape_jobs(
    site_name=["indeed", "linkedin", "zip_recruiter", "glassdoor"],
    search_term="software engineer",
    location="Dallas, TX",
    results_wanted=25,  # be wary the higher it is, the more likey you'll get blocked (rotating proxy can help tho)
    country_indeed="USA",
    # proxy="http://jobspy:5a4vpWtj8EeJ2hoYzk@ca.smartproxy.com:20001",
)

# formatting for pandas
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", 50)  # set to 0 to see full job url / desc

# 1: output to console
print(jobs)

# 2: output to .csv
jobs.to_csv("./jobs.csv", index=False)
print("outputted to jobs.csv")

# 3: output to .xlsx
# jobs.to_xlsx('jobs.xlsx', index=False)

# 4: display in Jupyter Notebook (1. pip install jupyter 2. jupyter notebook)
# display(jobs)