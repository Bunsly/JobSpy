from jobspy.model import CompensationInterval, JobType

jobs_per_page = 20

job_type_codes = {
    JobType.FULL_TIME: "employment_type:full_time",
    JobType.PART_TIME: "employment_type:part_time",
    JobType.CONTRACT: "employment_type:contract",
    JobType.TEMPORARY: "employment_type:temporary",
    JobType.PER_DIEM: "employment_type:as_needed",
    JobType.OTHER: "employment_type:other",
}

pay_intervals = {
    "PAY_INTERVAL_HOUR": CompensationInterval.HOURLY,
    "PAY_INTERVAL_DAY": CompensationInterval.DAILY,
    "PAY_INTERVAL_WEEK": CompensationInterval.WEEKLY,
    "PAY_INTERVAL_MONTH": CompensationInterval.MONTHLY,
    "PAY_INTERVAL_YEAR": CompensationInterval.YEARLY,
}

employment_type_names = (
    "UNSPECIFIED",
    "FULL_TIME",
    "PART_TIME",
    "CONTRACTOR",
    "TEMPORARY",
    "PER_DIEM",
    "OTHER",
    "INTERNSHIP",
)
location_type_names = (
    "UNSPECIFIED",
    "IN_PERSON",
    "REMOTE",
    "HYBRID",
    "REMOTE_OPTIONAL",
)
pay_interval_names = ("UNSPECIFIED", "HOUR", "DAY", "WEEK", "MONTH", "YEAR")
pay_currency_names = ("UNSPECIFIED", "AUD", "CAD", "EUR", "GBP", "USD")
