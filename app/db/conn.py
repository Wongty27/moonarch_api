import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from fastapi import Depends
from typing import Annotated, Literal
from google.cloud.sql.connector import Connector

load_dotenv("app/core/environment/.env")

class Base(DeclarativeBase):
    pass

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
# INSTANCE_NAME = os.getenv("INSTANCE_NAME")

# def gcloud_engine():
#     connector = Connector()
#     conn = connector.connect(
#         INSTANCE_NAME,
#         "psycopg2",
#         user=DB_USER,
#         password=DB_PASSWORD,
#         db=DB_NAME
#     )
#     return create_engine("postgresql+psycopg2://", creator=conn)

DB_URL = f"postgresql+pg8000://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DB_URL, pool_size=5, max_overflow=10, pool_timeout=30, pool_recycle=1800)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    database = SessionLocal()
    try:
        yield database
        database.execute(text('CREATE EXTENSION IF NOT EXISTS vector'))
    finally:
        database.close()

db_dependency = Annotated[Session, Depends(get_db)]