from sqlalchemy.types import TypeDecorator
from sqlalchemy import Integer, String, Text, types
from sqlalchemy.orm import mapped_column
from db import Base
from sqlalchemy.dialects.postgresql import TSVECTOR

class TSVector(TypeDecorator):
    impl = TSVECTOR

class Faq(Base):
    __tablename__ = "faq"

    id = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    question = mapped_column(Text, nullable=False)
    answer = mapped_column(Text, nullable=False)
    category = mapped_column(String, nullable=False)
    __ts_vector__ = mapped_column(TSVector)

# results = Videos.query.filter(Video.description.match(term)).all(), 