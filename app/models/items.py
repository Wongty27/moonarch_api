from app.models.main import Base
from sqlalchemy import Text, ForeignKey, Identity
# from sqlalchemy.dialects.postgresql import TSVECTOR
# from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import mapped_column, Mapped

class ItemType(Base):
    __tablename__ = "item_type"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str]

class Item(Base):
    __tablename__ = "item"

    id: Mapped[int] = mapped_column(Identity(start=10000), primary_key=True, index=True)
    type_id: Mapped[str] = mapped_column(ForeignKey("item_type.id")) # int or str?
    brand: Mapped[str] 
    name: Mapped[str]
    price: Mapped[float]
    quantity: Mapped[float]

# class ItemDetail(Base):
#     __tablename__ = "item_detail"

#     id: Mapped[int] = mapped_column(ForeignKey("item.id"), primary_key=True)
#     description: Mapped[str] = mapped_column(Text())
    