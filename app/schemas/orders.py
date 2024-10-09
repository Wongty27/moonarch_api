from pydantic import BaseModel, PositiveInt, Field
from typing import Literal
from datetime import datetime

class Order(BaseModel):
    id: PositiveInt = Field(gt=0)
    orders_list: dict
    customer_id: PositiveInt = Field(gt=0)
    created_at: datetime
    status: Literal["to pay", "to ship", "to receive", "delivered", "cancelled", "refund"]