from dotenv import load_dotenv
import os

load_dotenv()
# Google sheets output_format
GSHEET_NAME = os.environ.get("GSHEET_NAME", "JobSpy")
GSHEET_SECRET_JSON = os.environ.get("GSHEET_SECRET_JSON")

# optional auth
AUTH_REQUIRED = False
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = 60
ALGORITHM = "HS256"
