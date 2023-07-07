from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class JobType(Enum):
    FULL_TIME = 'full_time'
    PART_TIME = 'part_time'
    CONTRACT = 'contract'
    INTERNSHIP = 'internship'


class CompensationInterval(Enum):
    ANNUAL = 'annual'
    MONTHLY = 'monthly'
    WEEKLY = 'weekly'
    DAILY = 'daily'
    HOURLY = 'hourly'


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
    currency: str


class DeliveryEnum(Enum):
    EMAIL = 'email'
    URL = 'url'


class Delivery(BaseModel):
    method: DeliveryEnum
    value: str


class JobPost(BaseModel):
    title: str
    description: str
    company_name: str
    industry: str
    location: Location
    job_type: JobType
    compensation: Compensation
    date_posted: datetime
    delivery: Delivery = None


class JobResponse(BaseModel):
    jobs: list[JobPost]

    job_count: int

    page: int
    total_pages: int
