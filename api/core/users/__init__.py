from pydantic import BaseModel

class User(BaseModel):
    username: str
    full_name: str
    email: str
    disabled: bool


class UserInDB(User):
    hashed_password: str


class TokenData(BaseModel):
    username: str


class Token(BaseModel):
    access_token: str
    token_type: str
