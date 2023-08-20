from fastapi import APIRouter, Depends
from .jobs import router as jobs_router
from api.auth.auth_utils import get_active_current_user
from settings import AUTH_REQUIRED

if AUTH_REQUIRED:
    router = APIRouter(prefix="/v1", dependencies=[Depends(get_active_current_user)])
else:
    router = APIRouter(prefix="/v1")

router.include_router(jobs_router)
