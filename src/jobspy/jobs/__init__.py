from typing import Union, Optional
from datetime import date
from enum import Enum
from pydantic import BaseModel, validator


class JobType(Enum):
    FULL_TIME = (
        "fulltime",
        "períodointegral",
        "estágio/trainee",
        "cunormăîntreagă",
        "tiempocompleto",
        "vollzeit",
        "voltijds",
        "tempointegral",
        "全职",
        "plnýúvazek",
        "fuldtid",
        "دوامكامل",
        "kokopäivätyö",
        "tempsplein",
        "vollzeit",
        "πλήρηςαπασχόληση",
        "teljesmunkaidő",
        "tempopieno",
        "tempsplein",
        "heltid",
        "jornadacompleta",
        "pełnyetat",
        "정규직",
        "100%",
        "全職",
        "งานประจำ",
        "tamzamanlı",
        "повназайнятість",
        "toànthờigian",
    )
    PART_TIME = ("parttime", "teilzeit", "částečnýúvazek", "deltid")
    CONTRACT = ("contract", "contractor")
    TEMPORARY = ("temporary",)
    INTERNSHIP = (
        "internship",
        "prácticas",
        "ojt(onthejobtraining)",
        "praktikum",
        "praktik",
    )

    PER_DIEM = ("perdiem",)
    NIGHTS = ("nights",)
    OTHER = ("other",)
    SUMMER = ("summer",)
    VOLUNTEER = ("volunteer",)


class Country(Enum):
    ARGENTINA = ("argentina", "com.ar")
    AUSTRALIA = ("australia", "au", "com.au")
    AUSTRIA = ("austria", "at", "at")
    BAHRAIN = ("bahrain", "bh")
    BELGIUM = ("belgium", "be", "nl:be")
    BRAZIL = ("brazil", "br", "com.br")
    CANADA = ("canada", "ca", "ca")
    CHILE = ("chile", "cl")
    CHINA = ("china", "cn")
    COLOMBIA = ("colombia", "co")
    COSTARICA = ("costa rica", "cr")
    CZECHREPUBLIC = ("czech republic", "cz")
    DENMARK = ("denmark", "dk")
    ECUADOR = ("ecuador", "ec")
    EGYPT = ("egypt", "eg")
    FINLAND = ("finland", "fi")
    FRANCE = ("france", "fr", "fr")
    GERMANY = ("germany", "de", "de")
    GREECE = ("greece", "gr")
    HONGKONG = ("hong kong", "hk", "com.hk")
    HUNGARY = ("hungary", "hu")
    INDIA = ("india", "in", "co.in")
    INDONESIA = ("indonesia", "id")
    IRELAND = ("ireland", "ie", "ie")
    ISRAEL = ("israel", "il")
    ITALY = ("italy", "it", "it")
    JAPAN = ("japan", "jp")
    KUWAIT = ("kuwait", "kw")
    LUXEMBOURG = ("luxembourg", "lu")
    MALAYSIA = ("malaysia", "malaysia")
    MEXICO = ("mexico", "mx", "com.mx")
    MOROCCO = ("morocco", "ma")
    NETHERLANDS = ("netherlands", "nl", "nl")
    NEWZEALAND = ("new zealand", "nz", "co.nz")
    NIGERIA = ("nigeria", "ng")
    NORWAY = ("norway", "no")
    OMAN = ("oman", "om")
    PAKISTAN = ("pakistan", "pk")
    PANAMA = ("panama", "pa")
    PERU = ("peru", "pe")
    PHILIPPINES = ("philippines", "ph")
    POLAND = ("poland", "pl")
    PORTUGAL = ("portugal", "pt")
    QATAR = ("qatar", "qa")
    ROMANIA = ("romania", "ro")
    SAUDIARABIA = ("saudi arabia", "sa")
    SINGAPORE = ("singapore", "sg", "sg")
    SOUTHAFRICA = ("south africa", "za")
    SOUTHKOREA = ("south korea", "kr")
    SPAIN = ("spain", "es", "es")
    SWEDEN = ("sweden", "se")
    SWITZERLAND = ("switzerland", "ch", "de:ch")
    TAIWAN = ("taiwan", "tw")
    THAILAND = ("thailand", "th")
    TURKEY = ("turkey", "tr")
    UKRAINE = ("ukraine", "ua")
    UNITEDARABEMIRATES = ("united arab emirates", "ae")
    UK = ("uk", "uk", "co.uk")
    USA = ("usa", "www", "com")
    URUGUAY = ("uruguay", "uy")
    VENEZUELA = ("venezuela", "ve")
    VIETNAM = ("vietnam", "vn")

    # internal for ziprecruiter
    US_CANADA = ("usa/ca", "www")

    # internal for linkeind
    WORLDWIDE = ("worldwide", "www")

    @property
    def indeed_domain_value(self):
        return self.value[1]

    @property
    def glassdoor_domain_value(self):
        if len(self.value) == 3:
            subdomain, _, domain = self.value[2].partition(":")
            if subdomain and domain:
                return f"{subdomain}.glassdoor.{domain}"
            else:
                return f"www.glassdoor.{self.value[2]}"
        else:
            raise Exception(f"Glassdoor is not available for {self.name}")

    def get_url(self):
        return f"https://{self.glassdoor_domain_value}/"

    @classmethod
    def from_string(cls, country_str: str):
        """Convert a string to the corresponding Country enum."""
        country_str = country_str.strip().lower()
        for country in cls:
            if country.value[0] == country_str:
                return country
        valid_countries = [country.value for country in cls]
        raise ValueError(
            f"Invalid country string: '{country_str}'. Valid countries are: {', '.join([country[0] for country in valid_countries])}"
        )


class Location(BaseModel):
    country: Country | None = None
    city: Optional[str] = None
    state: Optional[str] = None

    def display_location(self) -> str:
        location_parts = []
        if self.city:
            location_parts.append(self.city)
        if self.state:
            location_parts.append(self.state)
        if self.country and self.country not in (Country.US_CANADA, Country.WORLDWIDE):
            if self.country.value[0] in ("usa", "uk"):
                location_parts.append(self.country.value[0].upper())
            else:
                location_parts.append(self.country.value[0].title())
        return ", ".join(location_parts)


class CompensationInterval(Enum):
    YEARLY = "yearly"
    MONTHLY = "monthly"
    WEEKLY = "weekly"
    DAILY = "daily"
    HOURLY = "hourly"


class Compensation(BaseModel):
    interval: Optional[CompensationInterval] = None
    min_amount: int | None = None
    max_amount: int | None = None
    currency: Optional[str] = "USD"


class JobPost(BaseModel):
    title: str
    company_name: str
    job_url: str
    location: Optional[Location]

    description: str | None = None
    company_url: str | None = None

    job_type: list[JobType] | None = None
    compensation: Compensation | None = None
    date_posted: date | None = None
    benefits: str | None = None
    emails: list[str] | None = None
    num_urgent_words: int | None = None
    is_remote: bool | None = None
    # company_industry: str | None = None


class JobResponse(BaseModel):
    jobs: list[JobPost] = []
