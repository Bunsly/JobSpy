from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class JobType(Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    TEMPORARY = "temporary"


class CompensationInterval(Enum):
    YEARLY = "yearly"
    MONTHLY = "monthly"
    WEEKLY = "weekly"
    DAILY = "daily"
    HOURLY = "hourly"


class Location(BaseModel):
    country: str
    city: str
    state: str
    postal_code: str = None
    address: str = None


class Compensation(BaseModel):
    interval: CompensationInterval
    min_amount: int
    max_amount: int
    currency: str = None


class DeliveryEnum(Enum):
    EMAIL = "email"
    URL = "url"


class Delivery(BaseModel):
    method: DeliveryEnum
    value: str


class JobPost(BaseModel):
    title: str
    description: str = None
    company_name: str
    industry: str = None
    location: Location
    job_type: JobType
    compensation: Compensation = None
    date_posted: datetime
    delivery: Delivery = None


class JobResponse(BaseModel):
    job_count: int
    page: int = 1
    total_pages: int

    jobs: list[JobPost]
