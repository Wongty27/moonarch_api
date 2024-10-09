import random
from db import Base
from sqlalchemy import Integer, String, Float, ForeignKey
from sqlalchemy.orm import DeclarativeBase, mapped_column

def random_quantity(start:int = 1, end:int = 100) -> int:
    return random.randint(start, end)

class Item(Base):
    __tablename__ = "item"

    id = mapped_column(String, primary_key=True, index=True) #, autoincrement=True)
    brand = mapped_column(String)
    model = mapped_column(String, nullable=False)

class ItemDetails(Base):
    __tablename__ = "details"

    id = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    item_id = mapped_column(String, ForeignKey("item.id"))
    price = mapped_column(Float, nullable=False)
    quantity = mapped_column(Integer, default=random_quantity(), nullable=False)
    description = mapped_column(String)