import random
from app.models.main import Base
from sqlalchemy import Text, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

def random_quantity(start:int = 1, end:int = 100) -> int:
    return random.randint(start, end)

def id_generator():
    pass

class ItemType(Base):
    __tablename__ = "itemtype"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str]

class Item(Base):
    __tablename__ = "item"
    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    # necessary?
    # item_id: Mapped[str] = mapped_column(default=id_generator(), unique=True)
    type: Mapped[str] = mapped_column(ForeignKey("itemtype.name"))
    brand: Mapped[str]
    name: Mapped[str]
    price: Mapped[float]
    quantity: Mapped[float] = mapped_column(default=random_quantity())

# combine item and itemdetail?
class ItemDetail(Base):
    __tablename__ = "itemdetail"

    id: Mapped[int] = mapped_column(ForeignKey("item.id"), primary_key=True)
    description = mapped_column(Text)