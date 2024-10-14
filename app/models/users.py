from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, mapped_column

class Base(DeclarativeBase):
    pass

class UserMaster(Base):
    __tablename__ = "user"

    id = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    username = mapped_column(String, nullable=False)
    hashed_password = mapped_column(String(30))