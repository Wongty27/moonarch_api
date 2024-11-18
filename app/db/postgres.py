import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends
from typing import Annotated

load_dotenv("app/.env")
# from google.cloud.sql.connector import Connector

# def gcloud_engine():
#     connector = Connector()
#     conn = connector.connect(
#         settings.INSTANCE_NAME,
#         "psycopg2",
#         user=settings.PG_USER,
#         password=settings.PG_PASSWORD,
#         db=settings.PG_DB_NAME
#     )
#     return create_engine("postgresql+psycopg2://", creator=conn)

DB_URL = f"postgresql+psycopg2://{os.getenv('PG_USER')}:admin@{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/{os.getenv('PG_DB_NAME')}"
engine = create_engine(
    DB_URL,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False, 
    bind=engine
)

def get_db():
    database = SessionLocal()
    try:
        yield database
        print(f"Connected to database.")
    finally:
        database.close()

db_dependency = Annotated[Session, Depends(get_db)]