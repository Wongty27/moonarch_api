from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import mapped_column
from datetime import datetime
from db import Base

class NewOrder(Base):
    __tablename__ = "new_order"

    id = mapped_column(Integer)
    customer_id = mapped_column(Integer, ForeignKey("user.id"))
    ordered_at = mapped_column(DateTime, nullable=False, default=datetime.now())
    