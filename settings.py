from dotenv import load_dotenv
import os

load_dotenv()
# gsheets (template to copy at https://docs.google.com/spreadsheets/d/1mOgb-ZGZy_YIhnW9OCqIVvkFwiKFvhMBjNcbakW7BLo/edit?usp=sharing)
GSHEET_NAME = os.environ.get("GSHEET_NAME", "JobSpy")

# optional autha
AUTH_REQUIRED = False
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = 60
ALGORITHM = "HS256"
