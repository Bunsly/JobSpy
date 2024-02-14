<img src="https://github.com/cullenwatson/JobSpy/assets/78247585/ae185b7e-e444-4712-8bb9-fa97f53e896b" width="400">

**JobSpy** is a simple, yet comprehensive, job scraping library.

**Not technical?** Try out the web scraping tool on our site at [usejobspy.com](https://usejobspy.com).

*Looking to build a data-focused software product?* **[Book a call](https://bunsly.com/)** *to
work with us.*

## Features

- Scrapes job postings from **LinkedIn**, **Indeed**, **Glassdoor**, & **ZipRecruiter** simultaneously
- Aggregates the job postings in a Pandas DataFrame
- Proxy support

[Video Guide for JobSpy](https://www.youtube.com/watch?v=RuP1HrAZnxs&pp=ygUgam9icyBzY3JhcGVyIGJvdCBsaW5rZWRpbiBpbmRlZWQ%3D) -
Updated for release v1.1.3

![jobspy](https://github.com/cullenwatson/JobSpy/assets/78247585/ec7ef355-05f6-4fd3-8161-a817e31c5c57)

### Installation

```
pip install python-jobspy
```

_Python version >= [3.10](https://www.python.org/downloads/release/python-3100/) required_

### Usage

```python
import csv
from jobspy import scrape_jobs

jobs = scrape_jobs(
    site_name=["indeed", "linkedin", "zip_recruiter", "glassdoor"],
    search_term="software engineer",
    location="Dallas, TX",
    results_wanted=20,
    hours_old=72, # (only linkedin is hour specific, others round up to days old)
    country_indeed='USA'  # only needed for indeed / glassdoor
)
print(f"Found {len(jobs)} jobs")
print(jobs.head())
jobs.to_csv("jobs.csv", quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False) # to_xlsx
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
├── site_type (List[enum]): linkedin, zip_recruiter, indeed, glassdoor
└── search_term (str)
Optional
├── location (int)
├── distance (int): in miles
├── job_type (enum): fulltime, parttime, internship, contract
├── proxy (str): in format 'http://user:pass@host:port'
├── is_remote (bool)
├── linkedin_fetch_description (bool): fetches full description for LinkedIn (slower)
├── results_wanted (int): number of job results to retrieve for each site specified in 'site_type'
├── easy_apply (bool): filters for jobs that are hosted on the job board site
├── linkedin_company_ids (list[int): searches for linkedin jobs with specific company ids
├── description_format (enum): markdown, html (format type of the job descriptions)
├── country_indeed (enum): filters the country on Indeed (see below for correct spelling)
├── offset (num): starts the search from an offset (e.g. 25 will start the search from the 25th result)
├── hours_old (int): filters jobs by the number of hours since the job was posted (all but LinkedIn rounds up to next day)
```

### JobPost Schema

```plaintext
JobPost
├── title (str)
├── company (str)
├── company_url (str)
├── job_url (str)
├── location (object)
│   ├── country (str)
│   ├── city (str)
│   ├── state (str)
├── description (str)
├── job_type (str): fulltime, parttime, internship, contract
├── compensation (object)
│   ├── interval (str): yearly, monthly, weekly, daily, hourly
│   ├── min_amount (int)
│   ├── max_amount (int)
│   └── currency (enum)
└── date_posted (date)
└── emails (str)
└── num_urgent_words (int)
└── is_remote (bool)
```

### Exceptions

The following exceptions may be raised when using JobSpy:

* `LinkedInException`
* `IndeedException`
* `ZipRecruiterException`
* `GlassdoorException`

## Supported Countries for Job Searching

### **LinkedIn**

LinkedIn searches globally & uses only the `location` parameter. You can only fetch 1000 jobs max from the LinkedIn endpoint we're using

### **ZipRecruiter**

ZipRecruiter searches for jobs in **US/Canada** & uses only the `location` parameter.

### **Indeed / Glassdoor**

Indeed & Glassdoor supports most countries, but the `country_indeed` parameter is required. Additionally, use the `location`
parameter to narrow down the location, e.g. city & state if necessary. 

You can specify the following countries when searching on Indeed (use the exact name, * indicates support for Glassdoor):

|                      |              |            |                |
|----------------------|--------------|------------|----------------|
| Argentina            | Australia*   | Austria*   | Bahrain        |
| Belgium*             | Brazil*      | Canada*    | Chile          |
| China                | Colombia     | Costa Rica | Czech Republic |
| Denmark              | Ecuador      | Egypt      | Finland        |
| France*              | Germany*     | Greece     | Hong Kong*     |
| Hungary              | India*       | Indonesia  | Ireland*       |
| Israel               | Italy*       | Japan      | Kuwait         |
| Luxembourg           | Malaysia     | Mexico*    | Morocco        |
| Netherlands*         | New Zealand* | Nigeria    | Norway         |
| Oman                 | Pakistan     | Panama     | Peru           |
| Philippines          | Poland       | Portugal   | Qatar          |
| Romania              | Saudi Arabia | Singapore* | South Africa   |
| South Korea          | Spain*       | Sweden     | Switzerland*   |
| Taiwan               | Thailand     | Turkey     | Ukraine        |
| United Arab Emirates | UK*          | USA*       | Uruguay        |
| Venezuela            | Vietnam      |            |                |


Glassdoor can only fetch 900 jobs from the endpoint we're using on a given search.
## Frequently Asked Questions

---

**Q: Encountering issues with your queries?**  
**A:** Try reducing the number of `results_wanted` and/or broadening the filters. If problems
persist, [submit an issue](https://github.com/Bunsly/JobSpy/issues).

---

**Q: Received a response code 429?**  
**A:** This indicates that you have been blocked by the job board site for sending too many requests. All of the job board sites are aggressive with blocking. We recommend:

- Waiting some time between scrapes (site-dependent).
- Trying a VPN or proxy to change your IP address.

---



  
