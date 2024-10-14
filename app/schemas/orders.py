from typing import Any
from pydantic import BaseModel, PositiveInt, Field, Json
from typing import Literal
from datetime import datetime

class OrderList(BaseModel):
    # json
    pass

class Order(BaseModel):
    id: PositiveInt = Field(gt=0)
    order_list: Json[Any] # OrderList
    customer_id: PositiveInt = Field(gt=0)
    order_time: datetime
    status: Literal["to pay", "to ship", "to receive", "delivered", "cancelled", "refund"]

class Feedback(BaseModel):
    id: PositiveInt = Field(gt=0)
    order_id: PositiveInt = Field(gt=0)
    rating: str = Field(default=5)
    platform: str
    description: str | None = None

# example
# order_list = {
#     "cpu": {"name": "brand+name", "quantity": 1, "price": 1200},
#     "gpu": {"name": "brand+name", "quantity": 1, "price": 1200},
#     "mobo": {"name": "brand+name", "quantity": 1, "price": 1200},
# }