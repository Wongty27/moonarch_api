from sqlalchemy import DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import mapped_column, DeclarativeBase, Mapped
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Order(Base):
    __tablename__ = "order"

    id: Mapped[int]
    order_list: Mapped[JSON]
    customer_email: Mapped[str]
    order_time: Mapped[DateTime] = mapped_column(default=datetime.now())
    status: Mapped[str]

class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("order.id"))
    rating: Mapped[int]
    platform: Mapped[str]
    description: Mapped[str]