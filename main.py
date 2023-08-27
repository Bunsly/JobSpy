from fastapi import FastAPI

from supabase_py import create_client, Client
from api import router as api_router

app = FastAPI(
    title="JobSpy Backend",
    description="Endpoints for job boardLinkedIn, Indeed, and ZipRecruiterscrapers",
    version="1.0.0",
)
app.include_router(api_router)

@app.get("/health", tags=["health"])
async def health_check():
    return {"message": "JobSpy ready to scrape"}
