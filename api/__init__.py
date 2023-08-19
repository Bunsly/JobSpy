from fastapi import APIRouter
from api.auth import router as auth_router
from .v1 import router as v1_router

router = APIRouter(
    prefix="/api",
)
router.include_router(v1_router)
router.include_router(auth_router)
