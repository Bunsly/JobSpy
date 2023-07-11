from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from api.core.users import Token
from api.auth.db_utils import authenticate_user
from api.auth.auth_utils import create_access_token

router = APIRouter(prefix="/token", tags=["token"])


@router.post("/", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    """
    Authenticates a user and provides an access token.
    :param form_data: OAuth2PasswordRequestForm object containing the user's credentials.
    :raises HTTPException: If the user cannot be authenticated.
    :return: A Token object containing the access token and the token type.
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token, token_type="bearer")
