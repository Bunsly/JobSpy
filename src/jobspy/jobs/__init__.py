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
    PART_TIME = ("parttime", "teilzeit")
    CONTRACT = ("contract", "contractor")
    TEMPORARY = ("temporary",)
    INTERNSHIP = ("internship", "prácticas", "ojt(onthejobtraining)", "praktikum")

    PER_DIEM = ("perdiem",)
    NIGHTS = ("nights",)
    OTHER = ("other",)
    SUMMER = ("summer",)
    VOLUNTEER = ("volunteer",)


class Country(Enum):
    ARGENTINA = ("argentina", "ar")
    AUSTRALIA = ("australia", "au")
    AUSTRIA = ("austria", "at")
    BAHRAIN = ("bahrain", "bh")
    BELGIUM = ("belgium", "be")
    BRAZIL = ("brazil", "br")
    CANADA = ("canada", "ca")
    CHILE = ("chile", "cl")
    CHINA = ("china", "cn")
    COLOMBIA = ("colombia", "co")
    COSTARICA = ("costa rica", "cr")
    CZECHREPUBLIC = ("czech republic", "cz")
    DENMARK = ("denmark", "dk")
    ECUADOR = ("ecuador", "ec")
    EGYPT = ("egypt", "eg")
    FINLAND = ("finland", "fi")
    FRANCE = ("france", "fr")
    GERMANY = ("germany", "de")
    GREECE = ("greece", "gr")
    HONGKONG = ("hong kong", "hk")
    HUNGARY = ("hungary", "hu")
    INDIA = ("india", "in")
    INDONESIA = ("indonesia", "id")
    IRELAND = ("ireland", "ie")
    ISRAEL = ("israel", "il")
    ITALY = ("italy", "it")
    JAPAN = ("japan", "jp")
    KUWAIT = ("kuwait", "kw")
    LUXEMBOURG = ("luxembourg", "lu")
    MALAYSIA = ("malaysia", "malaysia")
    MEXICO = ("mexico", "mx")
    MOROCCO = ("morocco", "ma")
    NETHERLANDS = ("netherlands", "nl")
    NEWZEALAND = ("new zealand", "nz")
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
    SINGAPORE = ("singapore", "sg")
    SOUTHAFRICA = ("south africa", "za")
    SOUTHKOREA = ("south korea", "kr")
    SPAIN = ("spain", "es")
    SWEDEN = ("sweden", "se")
    SWITZERLAND = ("switzerland", "ch")
    TAIWAN = ("taiwan", "tw")
    THAILAND = ("thailand", "th")
    TURKEY = ("turkey", "tr")
    UKRAINE = ("ukraine", "ua")
    UNITEDARABEMIRATES = ("united arab emirates", "ae")
    UK = ("uk", "uk")
    USA = ("usa", "www")
    URUGUAY = ("uruguay", "uy")
    VENEZUELA = ("venezuela", "ve")
    VIETNAM = ("vietnam", "vn")

    # internal for ziprecruiter
    US_CANADA = ("usa/ca", "www")

    # internal for linkeind
    WORLDWIDE = ("worldwide", "www")

    def __new__(cls, country, domain):
        obj = object.__new__(cls)
        obj._value_ = country
        obj.domain = domain
        return obj

    @property
    def domain_value(self):
        return self.domain

    @classmethod
    def from_string(cls, country_str: str):
        """Convert a string to the corresponding Country enum."""
        country_str = country_str.strip().lower()
        for country in cls:
            if country.value == country_str:
                return country
        valid_countries = [country.value for country in cls]
        raise ValueError(
            f"Invalid country string: '{country_str}'. Valid countries (only include this param for Indeed) are: {', '.join(valid_countries)}"
        )


class Location(BaseModel):
    country: Country = None
    city: Optional[str] = None
    state: Optional[str] = None

    def display_location(self) -> str:
        location_parts = []
        if self.city:
            location_parts.append(self.city)
        if self.state:
            location_parts.append(self.state)
        if self.country and self.country not in (Country.US_CANADA, Country.WORLDWIDE):
            if self.country.value in ("usa", "uk"):
                location_parts.append(self.country.value.upper())
            else:
                location_parts.append(self.country.value.title())
        return ", ".join(location_parts)


class CompensationInterval(Enum):
    YEARLY = "yearly"
    MONTHLY = "monthly"
    WEEKLY = "weekly"
    DAILY = "daily"
    HOURLY = "hourly"


class Compensation(BaseModel):
    interval: CompensationInterval
    min_amount: int = None
    max_amount: int = None
    currency: Optional[str] = "USD"


class JobPost(BaseModel):
    title: str
    company_name: str
    job_url: str
    location: Optional[Location]

    description: Optional[str] = None
    job_type: Optional[JobType] = None
    compensation: Optional[Compensation] = None
    date_posted: Optional[date] = None


class JobResponse(BaseModel):
    jobs: list[JobPost] = []
