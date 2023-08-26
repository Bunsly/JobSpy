from typing import Optional, Union

from passlib.context import CryptContext
from supabase_py import create_client, Client
from fastapi import HTTPException, status

from api.core.users import UserInDB
from settings import SUPABASE_URL, SUPABASE_KEY

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
if SUPABASE_URL:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def create_user(user_create: UserInDB):
    """
    Creates a new user record in the 'users' table in Supabase.

    :param user_create: The data of the user to be created.
    :raises HTTPException: If an error occurs while creating the user.
    :return: The result of the insert operation.
    """
    result = supabase.table("users").insert(user_create.dict()).execute()
    print(f"Insert result: {result}")

    if "error" in result and result["error"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"User could not be created due to {result['error']['message']}",
        )

    return result


def get_user(username: str) -> Optional[UserInDB]:
    """
    Retrieves a user from the 'users' table by their username.

    :param username: The username of the user to retrieve.
    :return: The user data if found, otherwise None.
    """
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


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verifies a password against a hashed password using the bcrypt hashing algorithm.

    :param password: The plaintext password to verify.
    :param hashed_password: The hashed password to compare against.
    :return: True if the password matches the hashed password, otherwise False.
    """
    return pwd_context.verify(password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hashes a password using the bcrypt hashing algorithm.

    :param password: The plaintext password to hash.
    :return: The hashed password
    """
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str) -> Union[UserInDB, bool]:
    """
    Authenticates a user based on their username and password.

    :param username: The username of the user to authenticate.
    :param password: The plaintext password to authenticate.
    :return: The authenticated user if the username and password are correct, otherwise False.
    """
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user
