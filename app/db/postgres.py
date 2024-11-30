import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from typing import Annotated
from fastapi import Depends
from dotenv import load_dotenv
# from google.cloud.sql.connector import Connector

load_dotenv('./app/.env')

#PostgreSQL
PG_USER = os.getenv("DB_USER")
PG_PASSWORD = os.getenv("DB_PASSWORD")
PG_HOST = os.getenv("DB_HOST")
PG_PORT = os.getenv("DB_PORT")
PG_DB_NAME = os.getenv("DB_NAME")
INSTANCE_NAME = os.getenv("INSTANCE_NAME")


# def gcloud_engine():
#     connector = Connector()
#     conn = connector.connect(
#         instance_connection_string=INSTANCE_NAME,
#         driver="pg8000",
#         user=PG_USER,
#         password=PG_PASSWORD,
#         db=PG_DB_NAME
#     )
#     return create_engine("postgresql+pg8000://", creator=conn)

# #gcloud engine
# # engine = gcloud_engine()

# localhost engine
SQLALCHEMY_DATABASE_URL = f"postgresql+pg8000://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB_NAME}"
engine = create_engine(SQLALCHEMY_DATABASE_URL,
                       pool_size=5,
                       max_overflow=10,
                       pool_timeout=30,
                       pool_recycle=1800,)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

#Cloud SQL
# DB_USER = os.environ.get("DB_USER", "postgres")
# DB_PASS = os.environ.get("DB_PASS", "admin")
# DB_NAME = os.environ.get("DB_NAME", "moonarchsql")
# INSTANCE_CONNECTION_NAME = os.environ.get("INSTANCE_CONNECTION_NAME", "gaia-capstone08-prd:us-central1:moonarch")

# def getconn():
#     connector = Connector()
#     conn = connector.connect(
#         INSTANCE_CONNECTION_NAME,
#         "pg8000",
#         user=DB_USER,
#         password=DB_PASS,
#         db=DB_NAME
#     )
#     return conn

# engine = create_engine(
#     "postgresql+pg8000://",
#     creator=getconn,
# )

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]