from typing import Literal
from pydantic import BaseModel, Field, PositiveInt, StrictStr,EmailStr, SecretStr

class UserAccount(BaseModel):
    id: PositiveInt = Field(gt=0)
    first_name: StrictStr = Field(max_length=30)
    last_name: StrictStr = Field(max_length=30)
    email: EmailStr = Field(max_length=40)
    phone_number: str
    address: str
    postcode: int = Field(max_length=5)
    city: StrictStr
    state: StrictStr
    country: StrictStr = Field(default="Malaysia")
    company_name: str | None = Field(default=None)
    password: SecretStr = Field(max_length=30)
    role: Literal["customer", "admin"] = Field(default="customer")
