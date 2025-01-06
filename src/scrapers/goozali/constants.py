from model.Position import Position
from .model import GoozaliColumn, GoozaliFieldChoice

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

job_post_column_names = ["id",
                         "date_posted",
                         "field",
                         "title",
                         "job_url",
                         "company_name",
                         "description",
                         "location",
                         "company_industry"]

fields = ["Product Management",
          "Data Analyst",
          "Data Science, ML & Algorithms",
          "Software Engineering",
          "QA",
          "Cybersecurity",
          "IT and System Administration",
          "Frontend Development",
          "DevOps",
          "UI/UX, Design & Content",
          "HR & Recruitment",
          "Mobile Development",
          "Hardware Engineering",
          "Embedded, Low Level & Firmware Engineering",
          "Customer Success",
          "Project Management",
          "Operations",
          "Finance",
          "Systems Engineering",
          "Marketing",
          "Sales",
          "Compliance, Legal & Policy",
          "C-Level",
          "Business Development",
          "Mechanical Engineering",
          "Natural Science",
          "Other"]

def create_position_to_goozali_field_map():
    """
    Creates a map with Position as keys and a list of relevant GoozaliFieldChoice as values.

    Returns:
        dict: A dictionary mapping Position to a list of GoozaliFieldChoice.
    """
    position_to_goozali_map = {
        Position.BACKEND_DEVELOPER: [GoozaliFieldChoice.SOFTWARE_ENGINEERING],
        Position.FULLSTACK_DEVELOPER: [GoozaliFieldChoice.SOFTWARE_ENGINEERING],
        Position.FRONTEND_DEVELOPER: [GoozaliFieldChoice.FRONTEND_DEVELOPMENT, GoozaliFieldChoice.SOFTWARE_ENGINEERING],
        Position.DATA_SCIENTIST: [GoozaliFieldChoice.DATA_SCIENCE_ML_ALGORITHMS],
        Position.DATA_ANALYST: [GoozaliFieldChoice.DATA_ANALYST],
        Position.PROJECT_MANAGER: [GoozaliFieldChoice.PROJECT_MANAGEMENT],
        Position.CLOUD_ENGINEER: [GoozaliFieldChoice.DEVOPS, GoozaliFieldChoice.IT_AND_SYSTEM_ADMINISTRATION],
        Position.CLOUD_ARCHITECT: [GoozaliFieldChoice.DEVOPS, GoozaliFieldChoice.IT_AND_SYSTEM_ADMINISTRATION],
        Position.UX_UI_DESIGNER: [GoozaliFieldChoice.UI_UX_DESIGN_CONTENT],
        Position.PRODUCT_MANAGER: [GoozaliFieldChoice.PRODUCT_MANAGEMENT],
        Position.DEV_OPS_ENGINEER: [GoozaliFieldChoice.DEVOPS],
        Position.BUSINESS_ANALYST: [GoozaliFieldChoice.BUSINESS_DEVELOPMENT],
        Position.CYBERSECURITY_ENGINEER: [GoozaliFieldChoice.CYBERSECURITY],
        Position.MACHINE_LEARNING_ENGINEER: [GoozaliFieldChoice.DATA_SCIENCE_ML_ALGORITHMS],
        Position.ARTIFICIAL_INTELLIGENCE_ENGINEER: [GoozaliFieldChoice.DATA_SCIENCE_ML_ALGORITHMS],
        Position.DATABASE_ADMINISTRATOR: [GoozaliFieldChoice.IT_AND_SYSTEM_ADMINISTRATION],
        Position.SYSTEMS_ADMINISTRATOR: [GoozaliFieldChoice.IT_AND_SYSTEM_ADMINISTRATION],
        Position.NETWORK_ENGINEER: [GoozaliFieldChoice.IT_AND_SYSTEM_ADMINISTRATION],
        Position.TECHNICAL_SUPPORT_SPECIALIST: [GoozaliFieldChoice.IT_AND_SYSTEM_ADMINISTRATION],
        Position.SALES_ENGINEER: [GoozaliFieldChoice.SALES],
        Position.SCRUM_MASTER: [GoozaliFieldChoice.PROJECT_MANAGEMENT],
        Position.IT_MANAGER: [GoozaliFieldChoice.IT_AND_SYSTEM_ADMINISTRATION],
    }
    return position_to_goozali_map

# Get the map
position_to_goozali_field_map = create_position_to_goozali_field_map()

# Key mapper: Extract 'name' as the key
def extract_goozali_column_name(column): return column.name if isinstance(
    column, GoozaliColumn) else None
