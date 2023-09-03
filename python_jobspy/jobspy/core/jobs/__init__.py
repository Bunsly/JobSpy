from typing import Union, Optional
from datetime import date
from enum import Enum

from pydantic import BaseModel, validator


class JobType(Enum):
    FULL_TIME = "fulltime"
    PART_TIME = "parttime"
    CONTRACT = "contract"
    TEMPORARY = "temporary"
    INTERNSHIP = "internship"

    PER_DIEM = "perdiem"
    NIGHTS = "nights"
    OTHER = "other"
    SUMMER = "summer"
    VOLUNTEER = "volunteer"



class Location(BaseModel):
    country: str = "USA"
    city: str = None
    state: Optional[str] = None


class CompensationInterval(Enum):
    YEARLY = "yearly"
    MONTHLY = "monthly"
    WEEKLY = "weekly"
    DAILY = "daily"
    HOURLY = "hourly"


class Compensation(BaseModel):
    interval: CompensationInterval
    min_amount: int = None
    max_amount: int = None
    currency: str = "USD"


class JobPost(BaseModel):
    title: str
    company_name: str
    job_url: str
    location: Optional[Location]

    description: str = None
    job_type: Optional[JobType] = None
    compensation: Optional[Compensation] = None
    date_posted: date = None


class JobResponse(BaseModel):
    success: bool
    error: str = None

    total_results: Optional[int] = None

    jobs: list[JobPost] = []

    returned_results: int = None

    @validator("returned_results", pre=True, always=True)
    def set_returned_results(cls, v, values):
        jobs_list = values.get("jobs")

        if v is None:
            if jobs_list is not None:
                return len(jobs_list)
            else:
                return 0
        return v
