from pydantic import BaseModel, Field, PositiveFloat, NonNegativeInt, PositiveInt, StrictStr
from typing import Literal

class ItemBase(BaseModel):
    id: PositiveInt = Field(gt=0)
    brand: str
    model: str
    price: PositiveFloat
    quantity: NonNegativeInt = Field(default=0, ge=0)
    description: str | None = None

class Case(ItemBase):
    color: str | None = None
    size: Literal["Mini-ITX", "mATX", "ATX"]
    psu_size: str | None = Field(default="atx")