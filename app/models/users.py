from sqlalchemy import Integer, String, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import mapped_column
from db import Base
from datetime import datetime
    
class User(Base):
    __tablename__ = "user"

    id = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    first_name = mapped_column(String, nullable=False)
    last_name = mapped_column(String, nullable=False)
    address = mapped_column(String, nullable=False)
    state = mapped_column(String, nullable=False)
    city = mapped_column(String, nullable=False)
    postcode = mapped_column(Integer, nullable=False)
    email = mapped_column(String, nullable=False, unique=True)
    phone_number = mapped_column(String, nullable=False, unique=True)
    hashed_password = mapped_column()
    role = mapped_column(String)
