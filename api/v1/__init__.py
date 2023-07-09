from fastapi import APIRouter, Depends
from .jobs import router as jobs_router
from api.auth.auth_utils import get_active_current_user

router = APIRouter(prefix="/v1", dependencies=[Depends(get_active_current_user)])
router.include_router(jobs_router)
