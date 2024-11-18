from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import mapped_column, Mapped
from datetime import datetime
# import json
from app.models.main import Base

class OrderModel(Base):
    __tablename__ = "order"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    # order_list: Mapped[json]
    customer_email: Mapped[str]
    order_time: Mapped[datetime] = mapped_column(default=func.now())
    status: Mapped[str]

class FeedbackModel(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("order.id"))
    rating: Mapped[int]
    platform: Mapped[str]
    description: Mapped[str]