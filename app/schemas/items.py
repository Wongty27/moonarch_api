from typing import Literal
from pydantic import BaseModel, Field

class ItemType(BaseModel):
    id: int
    name: Literal["cpu", "gpu", "mobo", "case", "fan", "cooler", "hdd" "ram", "psu"]

class Item(BaseModel):
    id: str
    # item_type: Literal["cpu", "gpu", "mobo", "case", "fan", "cooler", "hdd" "ram", "psu"]
    item_brand: str
    item_name: str
    price: float = Field(gt=0)
    stock_quantity: int = Field(ge=0)
    
class ItemDetail(BaseModel):
    id: int
    description: str | None = None