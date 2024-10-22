from fastapi import APIRouter
from pydantic import BaseModel, EmailStr, Field, PositiveFloat, NonNegativeInt, SecretStr, PositiveInt, StrictStr

router = APIRouter()

# def authenticate_user(email: EmailStr, password: SecretStr, db):
#     user = db.query()