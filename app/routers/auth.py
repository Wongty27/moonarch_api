import os
from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone
from app.db.postgres import db_dependency
from app.models import Users
from app.schemas import UserRequest, Token

router = APIRouter(prefix="/auth", tags=["Authentication"])

#oauth
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")  
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

def authenticate_user(email: str, password: str, db):
    user = db.query(Users).filter(Users.email == email).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.password):
        return False
    return user

def create_access_token(email: str, user_id: str, user_type: str, expires_delta: timedelta):
    encode = {
        "sub": email,
        "id": str(user_id),
        "user_type": user_type  # Include user_type in the token
    }
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user_id: str = payload.get("id")
        user_type: str = payload.get("user_type")  # Get user_type from token
        if email is None or user_id is None:
            raise HTTPException(status_code=401, detail="Could not validate user.")

        return {"email": email, "id": user_id, "user_type": user_type}

    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate user.")
    
current_user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/users", response_model=dict)
async def add_users(db: db_dependency, user_request: UserRequest):
    # Check if user exists
    existing_user = db.query(Users).filter(Users.email == user_request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered. Please use a different email or login."
        )

    try:
        # Create new user with only email and password
        new_user = Users(
            email=user_request.email,
            password=bcrypt_context.hash(user_request.password),
            # These will automatically be NULL in database
            full_name=None,
            phone_number=None,
            street_address=None,
            city=None,
            state=None,
            postcode=None,
            country=None
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Generate token for immediate login
        token = create_access_token(
            new_user.email, 
            str(new_user.user_id), 
            new_user.user_type, 
            timedelta(minutes=20)
        )

        return {
            "message": "User created successfully",
            "user": {
                "email": new_user.email,
                "user_id": str(new_user.user_id),
                "user_type": new_user.user_type
            },
            "access_token": token,
            "token_type": "bearer"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create user: {str(e)}"
        )

@router.post("/token", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    # Use form_data.username as email for authentication
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Could not validate user.")
    else:
        token = create_access_token(user.email, user.user_id, user.user_type, timedelta(minutes=20))
        return {"access_token": token, "token_type": "bearer"}

# Custom dependency to check if user is of type 'master'
async def master_required(current_user: current_user_dependency):
    if current_user["user_type"] != "master":
        raise HTTPException(status_code=403, detail="Access forbidden: Master access only.")
    return current_user

# Protect a route for 'customer' access only
async def customer_required(db: db_dependency, current_user: current_user_dependency):
    if current_user["user_type"] != "customer":
        raise HTTPException(status_code=403, detail="Access forbidden: Customer access only.")
    
    return current_user

