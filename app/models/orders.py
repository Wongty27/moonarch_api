from sqlalchemy import Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import mapped_column, DeclarativeBase
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Order(Base):
    __tablename__ = "order"

    id = mapped_column(Integer)
    order_list = mapped_column(JSON)
    customer_id = mapped_column(Integer, ForeignKey("user.id"))
    order_time = mapped_column(DateTime, nullable=False, default=datetime.now())
    status = mapped_column(String)

class Feedback(Base):
    __tablename__ = "feedback"

    id = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = mapped_column(Integer, ForeignKey("order.id"))
    rating = mapped_column(Integer, default=5)
    platform = mapped_column(String, nullable=False)
    description = mapped_column(Text)