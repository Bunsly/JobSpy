from passlib.context import CryptContext
from supabase_py import create_client, Client
from fastapi import HTTPException, status

from api.core.users import UserInDB
from settings import SUPABASE_URL, SUPABASE_KEY

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def create_user(user_create: UserInDB):
    result = supabase.table("users").insert(user_create.dict()).execute()
    print(f"Insert result: {result}")

    if "error" in result and result["error"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"User could not be created due to {result['error']['message']}",
        )

    return result


def get_user(username: str):
    result = supabase.table("users").select().eq("username", username).execute()

    if "error" in result and result["error"]:
        print(f"Error: {result['error']['message']}")
        return None
    else:
        if result["data"]:
            user_data = result["data"][0]
            return UserInDB(**user_data)
        else:
            return None


def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user
