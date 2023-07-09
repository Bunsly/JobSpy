from fastapi import APIRouter, HTTPException, status
from api.core.users import UserCreate, UserInDB
from api.auth.db_utils import get_user, get_password_hash, create_user

router = APIRouter(prefix="/register", tags=["register"])


@router.post("/")
async def register_new_user(user: UserCreate):
    existing_user = get_user(user.username)
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    hashed_password = get_password_hash(user.password)
    print(f"Hashed password: {hashed_password}")
    user_create = UserInDB(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        disabled=False,
    )
    create_user(user_create)

    return {"detail": "User created successfully"}
