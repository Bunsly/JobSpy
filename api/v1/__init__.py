from fastapi import APIRouter
from .jobs import router as jobs_router
from .token import router as token_router

router = APIRouter(prefix="/v1")
router.include_router(jobs_router)
router.include_router(token_router)
