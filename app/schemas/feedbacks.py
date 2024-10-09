from pydantic import BaseModel, Field, PositiveInt

class Feedback(BaseModel):
    order_id: PositiveInt = Field(gt=0)
    rating: str = Field(default=5)
    platform: str
    description: str | None = None