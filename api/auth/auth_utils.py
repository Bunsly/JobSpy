from datetime import datetime, timedelta

from jose import jwt, JWTError
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

from api.core.users import TokenData
from api.auth.db_utils import UserInDB, get_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


def create_access_token(data: dict) -> str:
    """
    Creates a JWT token based on the data provided.
    :param data
    :return: encoded_jwt
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Returns the current user associated with the provided JWT token.
    :param token
    :raises HTTPException: If the token is invalid or the user does not exist.
    :return: The UserInDB instance associated with the token.
    """
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credential_exception

    current_user = get_user(token_data.username)
    if current_user is None:
        raise credential_exception
    return current_user


async def get_active_current_user(current_user: UserInDB = Depends(get_current_user)):
    """
    Returns the current user if the user account is active.

    :param current_user: A UserInDB instance representing the current user.
    :raises HTTPException: If the user account is inactive.
    :return: The UserInDB instance if the user account is active.
    """
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user."
        )
    return current_user
