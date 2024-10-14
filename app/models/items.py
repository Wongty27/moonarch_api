import random
from sqlalchemy import Integer, String, Float, ForeignKey
from sqlalchemy.orm import DeclarativeBase, mapped_column

def random_quantity(start:int = 1, end:int = 100) -> int:
    return random.randint(start, end)

class Base(DeclarativeBase):
    pass

class ItemMaster(Base):
    __tablename__ = "item"

    id = mapped_column(String, primary_key=True, index=True)
    item_type = mapped_column(String, nullable=False)
    item_brand = mapped_column(String, nullable=False)
    item_name = mapped_column(String, nullable=False)
    stock_quantity = mapped_column(Integer,default=random_quantity(), nullable=False)

class ItemType(Base):
    __tablename__ = "itemtype"

    item_type_id = mapped_column(String, primary_key=True, index=True, autoincrement=True)
    item_type = mapped_column(String, ForeignKey("item.item_type"))
    

class ItemDetail(Base):
    __tablename__ = "itemdetails"

    id = mapped_column(String,  ForeignKey("item.id"), primary_key=True)
    description = mapped_column(String)

class ItemPrice(Base):
    __tablename__ = "itemprices"

    id = mapped_column(String,  ForeignKey("item.id"), primary_key=True)
    cost_price = mapped_column(Float)
    selling_price = mapped_column(Float)
