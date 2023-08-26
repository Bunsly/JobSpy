# JobSpy AIO Scraper

## Features

- Scrapes job postings from **LinkedIn**, **Indeed** & **ZipRecruiter** simultaneously
- Returns jobs with title, location, company, description & other data
- Optional JWT authorization


### API

POST `/api/v1/jobs/`
### Request Schema
#### Example
<pre>
{
    "site_type": ["linkedin", "indeed"],
    "search_term": "software engineer",
    "location": "austin, tx",
    "distance": 10,
    "job_type": "fulltime",
    "results_wanted": 10
}
</pre>

#### Parameters:
##### Required
- **site_type**: _List[str]_ - `linkedin`, `zip_recruiter`, `indeed`
- **search_term**: _str_

##### Optional
- **location**: _int_
- **distance**: _int_
- **job_type**: _str_ - `fulltime`, `parttime`, `internship`, `contract`
- **is_remote**: _bool_
- **results_wanted**: _int_ (per `site_type`)
- **easy_apply**: _bool_ (only for `linkedIn`)


## Response Schema
### Example
![image](https://github.com/cullenwatson/jobspy/assets/78247585/63b313db-ce25-41aa-9ffd-ae86af6f2a45)

#### JobResponse
- **success**: _bool_ - Indicates if the request was successful
- **error**: _str_
- **jobs**: _list[JobPost]_
  - #### JobPost
    - **title**: _str_ 
    - **company_name**: _str_ 
    - **job_url**: _str_ 
    - **location**: _object_ - (country, city, state, postal_code, address)
    - **description**: _str_ 
    - **job_type**: _str_ - `fulltime`, `parttime`, `internship`, `contract`
    - **compensation**: _object_ - Contains: `interval`, `min_amount`, `max_amount`, `currency`
    - **date_posted**: _str_
      
- **total_results**: _int_
- **returned_results**: _int_ 


## Installation
_Python >= 3.10 required_  
1. Clone this repository `git clone https://github.com/cullenwatson/jobspy`
2. Install the dependencies with `pip install -r requirements.txt`
4. Run the server with `uvicorn main:app --reload`

## Usage

To see the interactive API documentation, visit [localhost:8000/docs](http://localhost:8000/docs).

For Postman integration:
- Import the Postman collection and environment JSON files from the `/postman/` folder.


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

Use these endpoints to register and get an access token: 

![image](https://github.com/cullenwatson/jobspy/assets/78247585/c84c33ec-1fe8-4152-9c8c-6c4334aecfc3)

