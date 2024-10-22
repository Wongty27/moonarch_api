from typing import Any
from pydantic import BaseModel, EmailStr, Field, Json
from typing import Literal
from datetime import datetime

class OrderList(BaseModel):
    pass

class Order(BaseModel):
    id: int = Field(ge=1)
    order_list: Json[Any]
    customer_email: EmailStr
    order_time: datetime
    status: Literal["to pay", "to ship", "to receive", "delivered", "cancelled", "refund"]

class Feedback(BaseModel):
    id: int = Field(ge=1)
    order_id: int = Field(ge=1)
    rating: int
    platform: Literal["Facebook", "Instagram"]
    opinion: str | None = None

# example
# order_list = {
#     "cpu": {"name": "brand+name", "quantity": 1, "price": 1200},
#     "gpu": {"name": "brand+name", "quantity": 1, "price": 1200},
#     "mobo": {"name": "brand+name", "quantity": 1, "price": 1200},
# }