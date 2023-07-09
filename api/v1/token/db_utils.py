from passlib.context import CryptContext

from supabase_py import create_client, Client
from api.core.users import UserInDB
from settings import SUPABASE_URL, SUPABASE_KEY

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_user(username: str):
    result = supabase.table('users').select().eq('username', username).execute()

    if 'error' in result and result['error']:
        print(f"Error: {result['error']['message']}")
        return None
    else:
        if result['data']:
            user_data = result['data'][0]  # get the first (and should be only) user with the matching username
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
