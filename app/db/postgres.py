from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from google.cloud.sql.connector import Connector

import os
from dotenv import load_dotenv

load_dotenv('app/.env')

#PostgreSQL
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT")
PG_DB_NAME = os.getenv("PG_DB_NAME")
INSTANCE_NAME = os.getenv("INSTANCE_NAME")

def gcloud_engine():
    connector = Connector()
    conn = connector.connect(
        instance_connection_string=INSTANCE_NAME,
        driver="pg8000",
        user=PG_USER,
        password=PG_PASSWORD,
        db=PG_DB_NAME
    )
    return create_engine("postgresql+pg8000://", creator=conn)

#gcloud engine
# engine = gcloud_engine()

# localhost engine
SQLALCHEMY_DATABASE_URL = f"postgresql+pg8000://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB_NAME}"
engine = create_engine(SQLALCHEMY_DATABASE_URL,
                       pool_size=5,
                       max_overflow=10,
                       pool_timeout=30,
                       pool_recycle=1800,)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]