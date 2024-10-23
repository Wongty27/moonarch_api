from sqlalchemy import Text
from main import Base
from sqlalchemy.orm import mapped_column, Mapped
# from sqlalchemy.dialects.postgresql import TSVECTOR

class Faq(Base):
    __tablename__ = "faq"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    question = mapped_column(Text)
    answer = mapped_column(Text)
    category: Mapped[str]