from typing import Union
from datetime import datetime
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


class Location(BaseModel):
    country: str = "USA"
    city: str = None
    state: str = None


class CompensationInterval(Enum):
    YEARLY = "yearly"
    MONTHLY = "monthly"
    WEEKLY = "weekly"
    DAILY = "daily"
    HOURLY = "hourly"


class Compensation(BaseModel):
    interval: CompensationInterval
    min_amount: float
    max_amount: float
    currency: str = "USA"


class JobPost(BaseModel):
    title: str
    company_name: str
    job_url: str
    location: Location

    description: str = None
    job_type: JobType = None
    compensation: Compensation = None
    date_posted: datetime = None


class JobResponse(BaseModel):
    success: bool
    error: str = None

    jobs: list[JobPost] = []

    total_results: int = None
    returned_results: int = None

    @validator("returned_results")
    def set_returned_results(cls, v, values):
        if v is None and values.get("jobs"):
            return len(values["jobs"])
        return v
