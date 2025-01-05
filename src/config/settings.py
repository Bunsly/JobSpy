import os

from pydantic_settings import BaseSettings, SettingsConfigDict

if not os.getenv("ENV"):
    raise ValueError("Invalid environment. Set the 'ENV' variable (e.g., export ENV=dev).")

dotenv_file = os.path.join(os.path.dirname(__file__), ".env." + os.environ.get("ENV"))

if not os.path.exists(dotenv_file):
    raise FileNotFoundError(f"Environment file not found: {dotenv_file}")


class Settings(BaseSettings):
    env: str
    telegram_api_token: str
    mongo_uri: str
    mongo_db_name: str
    print(f"Loading environment from: {dotenv_file}")
    model_config = SettingsConfigDict(
        env_file=dotenv_file
    )


settings = Settings()
