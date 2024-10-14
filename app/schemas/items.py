from typing import Literal
from pydantic import BaseModel, Field, PositiveFloat, NonNegativeInt, StrictStr

class ItemMaster(BaseModel):
    id: str
    item_type: Literal["cpu", "gpu", "mobo", "case", "fan", "cooler", "hdd" "ram", "psu"]
    item_brand: str
    item_name: str
    stock_quantity: NonNegativeInt = Field(ge=0)

class ItemType(BaseModel):
    item_type_id: int
    item_type: Literal["cpu", "gpu", "mobo", "case", "fan", "cooler", "hdd" "ram", "psu"]
    
class ItemDetail(BaseModel):
    id: str
    description: str | None = None

class ItemPrice(BaseModel):
    id: str
    cost_price: PositiveFloat = Field(gt=0)
    selling_price: PositiveFloat = Field(gt=0)

