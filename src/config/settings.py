import os

from pydantic import Field
from pydantic_settings import BaseSettings

if not os.environ.get("ENV"):
    raise ValueError("Invalid environment. Set the 'ENV' variable (e.g., export ENV=dev).")


class Settings(BaseSettings):
    telegram_api_token: str = Field(alias="telegram_api_token")
    mongo_uri: str = Field(alias="mongo_uri")
    mongo_db_name: str = Field(alias="mongo_db_name")


settings = Settings()
