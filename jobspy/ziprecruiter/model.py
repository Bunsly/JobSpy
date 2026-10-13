from pydantic import AliasPath, BaseModel, Field


class TypeName(BaseModel):
    name: str


class ApplyButtonConfig(BaseModel):
    externalApplyUrl: str | None = None


class Pay(BaseModel):
    visible: bool | None = Field(
        default=None, validation_alias=AliasPath("metadata", "visible")
    )
    interval: str | None = None
    min: float | None = None
    max: float | None = None
    currency: str | None = None


class Job(BaseModel):
    listingKey: str | None
    title: str
    postedAtUtc: str = Field(validation_alias=AliasPath("status", "postedAtUtc"))
    employmentTypes: list[TypeName]
    countryCode: str | None = Field(
        validation_alias=AliasPath("location", "countryCode")
    )
    city: str | None = Field(
        default=None, validation_alias=AliasPath("location", "city")
    )
    stateCode: str | None = Field(
        default=None, validation_alias=AliasPath("location", "stateCode")
    )
    applyButtonConfig: ApplyButtonConfig
    name: str | None = Field(validation_alias=AliasPath("company", "name"))
    companyUrl: str | None
    logoUrl: str | None = Field(
        default=None, validation_alias=AliasPath("companyLogo", "logoUrl")
    )
    rawCanonicalZipJobPageUrl: str
    locationTypes: list[TypeName]
    pay: Pay


class JobSearch(BaseModel):
    jobKeysMap: dict[str, object]
    jobCount: int


class JobDetails(BaseModel):
    htmlFullDescription: str | None
    about: str | None = Field(
        default=None, validation_alias=AliasPath("companyWidget", "about")
    )
    canonicalIndustries: list[str] | None = Field(
        default=None, validation_alias=AliasPath("companyWidget", "canonicalIndustries")
    )
    canonicalWebsite: str | None = Field(
        default=None, validation_alias=AliasPath("companyWidget", "canonicalWebsite")
    )
    companySizeDisplay: str | None = Field(
        default=None, validation_alias=AliasPath("companyWidget", "companySizeDisplay")
    )
    hqLocation: str | None = Field(
        default=None, validation_alias=AliasPath("companyWidget", "hqLocation")
    )
    description: str | None = Field(
        default=None, validation_alias=AliasPath("breakroomCompany", "description")
    )
    rating: float | None = Field(
        default=None, validation_alias=AliasPath("breakroomCompany", "rating")
    )
