from fastapi import APIRouter
from .jobs import router as jobs_router

router = APIRouter(prefix="/v1")
router.include_router(jobs_router)
