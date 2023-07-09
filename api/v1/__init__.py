from fastapi import APIRouter, Depends
from .jobs import router as jobs_router
from api.auth.token import router as token_router
from api.auth.auth_utils import get_active_current_user

router = APIRouter(prefix="/v1", dependencies=[Depends(get_active_current_user)])
router.include_router(jobs_router)
router.include_router(token_router)
