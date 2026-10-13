from pydantic import AliasPath, BaseModel, Field


class Job(BaseModel):
    Jobid: str
    publishDate: str
    WorkPlace: str | None
    location: str | None
    jobTitle: str
    companyName: str | None
    JobType: str
    Salary: str
    logoUrl: str | None
    Vacancies: int | None
    experience: str | None


class JobSearch(BaseModel):
    data: list[dict[str, object]]
    premiumData: list[dict[str, object]] | None = None
    totalpages: int = Field(validation_alias=AliasPath("common", "totalpages"))


class Details(BaseModel):
    JobKeyPoints: str | None
    JobDescription: str | None
    EducationRequirements: str | None
    experience: str | None
    AdditionJobRequirements: str | None
    JobOtherBenifits: str | None
    ApplyInstruction: str | None
    ApplyEmail: str | None
    HardCopy: str | None
    WalkInInterview: str | None
    SkillsRequired: str | None
    CompanyID: str | None
    HaveAliasName: bool | None
    CompanyWeb: str
    ApplyURL: str
    CompanyAddress: str | None
    CompanyBusiness: str | None


class JobDetails(BaseModel):
    data: list[Details] | None
    message: str | None = None
