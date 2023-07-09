from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class JobType(Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contractor"
    INTERNSHIP = "internship"
    TEMPORARY = "temporary"
    PER_DIEM = "per_diem"
    NIGHTS = "nights"


class Location(BaseModel):
    country: str
    city: str = None
    state: str = None
    postal_code: str = None
    address: str = None


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
    currency: str = "US"


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
    location: Location
    job_type: JobType = None
    compensation: Compensation = None
    date_posted: datetime
    delivery: Delivery = None


class JobResponse(BaseModel):
    job_count: int
    page: int = 1
    total_pages: int

    jobs: list[JobPost]
