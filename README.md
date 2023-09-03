# <img src="https://github.com/cullenwatson/JobSpy/assets/78247585/2f61a059-9647-4a9c-bfb9-e3a9448bdc6a" style="vertical-align: sub; margin-right: 5px;"> JobSpy

**JobSpy** is a simple, yet comprehensive, job scraping library.
## Features

- Scrapes job postings from **LinkedIn**, **Indeed** & **ZipRecruiter** simultaneously
- Aggregates the job postings in a Pandas DataFrame

### Installation
`pip install python-jobspy`  
  
  _Python version >= [3.10](https://www.python.org/downloads/release/python-3100/) required_ 

### Usage

```python
from jobspy import scrape_jobs
import pandas as pd

jobs: pd.DataFrame = scrape_jobs(
    site_name=["indeed", "linkedin", "zip_recruiter"],
    search_term="software engineer",
    results_wanted=10
)

if jobs.empty:
    print("No jobs found.")
else:
    # 1 print
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 50)  # set to 0 to see full job url / desc
    print(jobs)

    # 2 display in Jupyter Notebook
    # display(jobs)

    # 3 output to csv
    # jobs.to_csv('jobs.csv', index=False)
```

### Output
```
SITE           TITLE                             COMPANY_NAME      CITY          STATE  JOB_TYPE  INTERVAL  MIN_AMOUNT  MAX_AMOUNT  JOB_URL                                            DESCRIPTION
indeed         Software Engineer                 AMERICAN SYSTEMS  Arlington     VA     None      yearly    200000      150000      https://www.indeed.com/viewjob?jk=5e409e577046...  THIS POSITION COMES WITH A 10K SIGNING BONUS!...
indeed         Senior Software Engineer          TherapyNotes.com  Philadelphia  PA     fulltime  yearly    135000      110000      https://www.indeed.com/viewjob?jk=da39574a40cb...  About Us TherapyNotes is the national leader i...
linkedin       Software Engineer - Early Career  Lockheed Martin   Sunnyvale     CA     fulltime  yearly    None        None        https://www.linkedin.com/jobs/view/3693012711      Description:By bringing together people that u...
linkedin       Full-Stack Software Engineer      Rain              New York      NY     fulltime  yearly    None        None        https://www.linkedin.com/jobs/view/3696158877      Rain’s mission is to create the fastest and ea...
zip_recruiter Software Engineer - New Grad       ZipRecruiter      Santa Monica  CA     fulltime  yearly    130000      150000      https://www.ziprecruiter.com/jobs/ziprecruiter...  We offer a hybrid work environment. Most US-ba...
zip_recruiter Software Developer                 TEKsystems        Phoenix       AZ     fulltime  hourly    65          75          https://www.ziprecruiter.com/jobs/teksystems-0...  Top Skills' Details• 6 years of Java developme...
```
### Parameters for `scrape_jobs()`


```plaintext
Required
├── site_type (List[enum]): linkedin, zip_recruiter, indeed
└── search_term (str)
Optional
├── location (int)
├── distance (int): in miles
├── job_type (enum): fulltime, parttime, internship, contract
├── is_remote (bool)
├── results_wanted (int): number of job results to retrieve for each site specified in 'site_type'
├── easy_apply (bool): filters for jobs on LinkedIn that have the 'Easy Apply' option
```

### JobPost Schema
```plaintext
JobPost
├── title (str)
├── company_name (str)
├── job_url (str)
├── location (object)
│   ├── country (str)
│   ├── city (str)
│   ├── state (str)
├── description (str)
├── job_type (enum)
├── compensation (object)
│   ├── interval (CompensationInterval): yearly, monthly, weekly, daily, hourly
│   ├── min_amount (float)
│   ├── max_amount (float)
│   └── currency (str)
└── date_posted (datetime)

```


### FAQ
  
#### Encountering issues with your queries?
  
Try reducing the number of `results_wanted` and/or broadening the filters. If problems persist, please submit an issue.
  
#### Received a response code 429?
This means you've been blocked by the job board site for sending too many requests. Consider waiting a few seconds, or try using a VPN. Proxy support coming soon.
  
