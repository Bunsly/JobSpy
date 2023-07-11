# JobSpy Backend

JobSpy Backend is a RESTful API built with FastAPI that allows users to scrape job postings from various job boards such as LinkedIn, Indeed, and ZipRecruiter.

## Features

- User authentication and token-based authorization
- Scraping job postings from LinkedIn, Indeed, and ZipRecruiter
- Detailed job data including title, location, company, and more

## Endpoints

- `/api/v1/jobs/`: POST endpoint to scrape jobs. Accepts parameters for site_type (job board), search term, location, distance, and results wanted.
- `/api/auth/token/`: POST endpoint for user authentication. Returns an access token.
- `/api/auth/register/`: POST endpoint to register a new user.
- `/health`: GET endpoint for a simple health check of the application.

## Installation

1. Clone this repository.
2. Install the dependencies with `pip install -r requirements.txt`.
3. Run the server with `uvicorn main:app --reload`.

## Usage

Visit http://localhost:8000/docs in your web browser to see the automatic interactive API documentation.

