from fastapi import APIRouter

from api.auth.token import router as token_router
from api.auth.register import router as register_router

router = APIRouter(prefix="/auth", tags=["auth"])
router.include_router(token_router)
router.include_router(register_router)
