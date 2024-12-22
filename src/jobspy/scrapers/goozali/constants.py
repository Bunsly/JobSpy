from jobspy.scrapers.goozali.model import GoozaliColumn


job_post_column_to_goozali_column = {
    "date_posted": "Discovered",
    "field": "Field",
    "title": "Job Title",
    "job_url": "Position Link",
    "company_name": "Company",
    "description": "Requirements",
    "location": "Location",
    "company_industry": "Company Industry",
    "id": "Job ID"
}

CHOICE_FIELD_KEY = "Software Engineering"

job_post_column_names = ["id",
                         "date_posted",
                         "field",
                         "title",
                         "job_url",
                         "company_name",
                         "description",
                         "location",
                         "company_industry"]


# Key mapper: Extract 'name' as the key
def extract_goozali_column_name(column): return column.name if isinstance(
    column, GoozaliColumn) else None
