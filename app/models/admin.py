from sqlalchemy import String
from main import Base
from sqlalchemy.orm import mapped_column, Mapped

class Admin(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    username: Mapped[str]
    hashed_password = mapped_column(String(30))