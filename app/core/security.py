import jwt
import secrets
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(username: str, user_id: int, expires_date: timedelta):
    encode = {"sub": username, "id": user_id}

    expires = datetime.now(timezone.utc) + expires_date
    encode.update({"exp": expires})
    return jwt.encode(encode, algorithm="HS256")