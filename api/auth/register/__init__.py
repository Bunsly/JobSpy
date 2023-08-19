from fastapi import APIRouter, HTTPException, status
from api.core.users import UserCreate, UserInDB
from api.auth.db_utils import get_user, get_password_hash, create_user

router = APIRouter(prefix="/register")


@router.post("/", response_model=dict)
async def register_new_user(user: UserCreate) -> dict:
    """
    Creates new user
    :param user:
    :raises HTTPException: If the username already exists.
    :return: A dictionary containing a detail key with a success message.
    """
    existing_user = get_user(user.username)
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    hashed_password = get_password_hash(user.password)
    user_create = UserInDB(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        disabled=False,
    )
    create_user(user_create)

    return {"detail": "User created successfully"}
