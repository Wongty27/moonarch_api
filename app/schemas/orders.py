from typing import Any
from pydantic import BaseModel, EmailStr, Field
from typing import Literal
from datetime import datetime

class OrderSchema(BaseModel):
    id: int = Field(ge=1)
    # order_list: json[Any]
    customer_email: EmailStr
    order_time: datetime
    status: Literal["to pay", "to ship", "to receive", "delivered", "cancelled", "refund"]

class FeedbackSchema(BaseModel):
    id: int = Field(ge=1)
    order_id: int = Field(ge=1)
    rating: int
    platform: Literal["Facebook", "Instagram"]
    opinion: str | None = None