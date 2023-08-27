# JobSpy AIO Scraper

## Features

- Scrapes job postings from **LinkedIn**, **Indeed** & **ZipRecruiter** simultaneously
- Returns jobs as JSON or CSV with title, location, company, description & other data
- Optional JWT authorization


### API

POST `/api/v1/jobs/`
### Request Schema

```plaintex
Required
├── site_type (List[enum]): linkedin, zip_recruiter, indeed
└── search_term (str)
Optional
├── location (int)
├── distance (int)
├── job_type (enum): fulltime, parttime, internship, contract
├── is_remote (bool)
├── results_wanted (int): per site_type
├── easy_apply (bool): only for linkedin
└── output_format (enum): json, csv
```

### Request Example
```json
"site_type": ["indeed", "linkedin"],
"search_term": "software engineer",
"location": "austin, tx",
"distance": 10,
"job_type": "fulltime",
"results_wanted": 15
```

### Response Schema
```plaintext
site_type (enum): 
JobResponse
├── success (bool)
├── error (str)
├── jobs (List[JobPost])
│   └── JobPost
│       ├── title (str)
│       ├── company_name (str)
│       ├── job_url (str)
│       ├── location (object)
│       │   ├── country (str)
│       │   ├── city (str)
│       │   ├── state (str)
│       ├── description (str)
│       ├── job_type (enum)
│       ├── compensation (object)
│       │   ├── interval (CompensationInterval): yearly, monthly, weekly, daily, hourly
│       │   ├── min_amount (float)
│       │   ├── max_amount (float)
│       │   └── currency (str)
│       └── date_posted (datetime)
│
├── total_results (int)
└── returned_results (int) 
```

### Response Example (JSON)
```json
{
    "indeed": {
        "success": true,
        "error": null,
        "jobs": [
            {
                "title": "Software Engineer",
                "company_name": "INTEL",
                "job_url": "https://www.indeed.com/jobs/viewjob?jk=a2cfbb98d2002228",
                "location": {
                    "country": "USA",
                    "city": "Austin",
                    "state": "TX",
                },
                "description": "Job Description Designs, develops, tests, and debugs..."
                "job_type": "fulltime",
                "compensation": {
                    "interval": "yearly",
                    "min_amount": 209760.0,
                    "max_amount": 139480.0,
                    "currency": "USD"
                },
                "date_posted": "2023-08-18T00:00:00"
            }, ...
        ],
        "total_results": 845,
        "returned_results": 15
    },
    "linkedin": {
        "success": true,
        "error": null,
        "jobs": [
            {
                "title": "Software Engineer 1",
                "company_name": "Public Partnerships | PPL",
                "job_url": "https://www.linkedin.com/jobs/view/3690013792",
                "location": {
                    "country": "USA",
                    "city": "Austin",
                    "state": "TX",
                },
                "description": "Public Partnerships LLC supports individuals with disabilities..."
                "job_type": null,
                "compensation": null,
                "date_posted": "2023-07-31T00:00:00"
            }, ...
        ],
        "total_results": 2000,
        "returned_results": 15
    }
}
```
### Response Example (CSV)
```
Site, Title, Company Name, Job URL, Country, City, State, Job Type, Compensation Interval, Min Amount, Max Amount, Currency, Date Posted, Description
indeed, Software Engineer, INTEL, https://www.indeed.com/jobs/viewjob?jk=a2cfbb98d2002228, USA, Austin, TX, fulltime, yearly, 209760.0, 139480.0, USD, 2023-08-18T00:00:00, Job Description Designs...
linkedin, Software Engineer 1, Public Partnerships | PPL, https://www.linkedin.com/jobs/view/3690013792, USA, Austin, TX, , , , , , 2023-07-31T00:00:00, Public Partnerships LLC supports...
```

## Installation
_Python version >= [3.10](https://www.python.org/downloads/release/python-3100/) required_  
1. Clone this repository `git clone https://github.com/cullenwatson/jobspy`
2. Install the dependencies with `pip install -r requirements.txt`
4. Run the server with `uvicorn main:app --reload`

## Usage

### Swagger UI:
To interact with the API documentation, navigate to [localhost:8000/docs](http://localhost:8000/docs).

### Postman:
To use Postman:
1. Locate the files in the `/postman/` directory.
2. Import the Postman collection and environment JSON files.

## FAQ

### I'm having issues with my queries. What should I do?

Try reducing the number of `results_wanted` and/or broadening the filters. If issues still persist, feel free to submit an issue. 

### I'm getting response code 429. What should I do?
You have been blocked by the job board site for sending too many requests. Wait a couple seconds or use a VPN.

### How to enable auth?

Change `AUTH_REQUIRED` in `/settings.py` to `True`

The auth uses [supabase](https://supabase.com). Create a project with a `users` table and disable RLS.  
  
<img src="https://github.com/cullenwatson/jobspy/assets/78247585/03af18e1-5386-49ad-a2cf-d34232d9d747" width="500">


Add these three environment variables:

- `SUPABASE_URL`: go to project settings -> API -> Project URL  
- `SUPABASE_KEY`: go to project settings -> API -> service_role secret
- `JWT_SECRET_KEY` - type `openssl rand -hex 32` in terminal to create a 32 byte secret key

Use these endpoints to register and get an access token: 

![image](https://github.com/cullenwatson/jobspy/assets/78247585/c84c33ec-1fe8-4152-9c8c-6c4334aecfc3)

