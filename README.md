# JobSpy Scraper

## Features

- Scrapes job postings from **LinkedIn**, **Indeed**, **ZipRecruiter**
- Returns jobs with title, location, company, and other data
- JWT authorization
  
![jobspy](https://github.com/cullenwatson/jobspy/assets/78247585/25e66a30-f151-4a68-90b7-dc5874260ee1)

## Endpoints
![image](https://github.com/cullenwatson/jobspy/assets/78247585/22c8840d-41e5-4b56-998b-3979787ad76c)


### Jobs Endpoint

**Endpoint**: `/api/v1/jobs/`

#### Parameters:
- **site_type**: str (Required) - Options: `linkedin`, `zip_recruiter`, `indeed`
- **search_term**: str (Required)
- **location**: int
- **distance**: int
- **job_type**: str - Options: `fulltime`, `parttime`, `internship`, `contract`
- **is_remote**: bool
- **results_wanted**: int
- **easy_apply**: bool (Only for LinkedIn)

### Example
![image](https://github.com/cullenwatson/jobspy/assets/78247585/0e52db2d-ed6b-44e5-8ece-16de707f33ec)


## Response

### Schema

#### JobResponse
- **success**: bool - Indicates if the request was successful
- **error**: str - Any error messages, null if no error
- **jobs**: list[JobPost] - A list of job postings
- **total_results**: int - Total number of results found
- **returned_results**: int - Number of results returned in this request

#### JobPost
- **title**: str 
- **company_name**: str 
- **job_url**: str 
- **location**: object - (country, city, state, postal_code, address)
- **description**: str 
- **job_type**: str - Options: `fulltime`, `parttime`, `internship`, `contract`
- **compensation**: object - Contains: `interval`, `min_amount`, `max_amount`, `currency`
- **date_posted**: str

### Example
![image](https://github.com/cullenwatson/jobspy/assets/78247585/73cb4423-8a53-456a-9da5-9ce7c56d5282)

## Installation
_Python >= 3.10 required_  
1. Clone this repository
2. Install the dependencies with `pip install -r requirements.txt`
4. Run the server with `uvicorn main:app --reload`

## Usage

Visit [http://localhost:8000/docs](http://localhost:8000/docs) to see the interactive API documentation.

## FAQ

### I'm having issues with my queries. What should I do?

Broadening your filters can often help. Additionally, try reducing the number of `results_wanted`.  
If issues still persist, feel free to submit an issue.

### How to enable auth?

Change `AUTH_REQUIRED` in `/settings.py` to `True`

The auth uses [supabase](https://supabase.com). Create a project with a `users` table and disable RLS.  
  
<img src="https://github.com/cullenwatson/jobspy/assets/78247585/03af18e1-5386-49ad-a2cf-d34232d9d747" width="500">


Add these three environment variables:

- `SUPABASE_URL`: go to project settings -> API -> Project URL  
- `SUPABASE_KEY`: go to project settings -> API -> service_role secret
- `JWT_SECRET_KEY` - type `openssl rand -hex 32` in terminal to create a 32 byte secret key
