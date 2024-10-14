from pydantic import BaseModel
from typing import Literal

class Faq(BaseModel):
    id: int
    question: str
    answer: str
    # category to be finalized
    category: Literal["Delivery", "Order", "Service", "Basic"]