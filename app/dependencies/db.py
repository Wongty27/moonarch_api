from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from fastapi import Depends
from typing import Annotated

Base = declarative_base()

# Create an engine to connect to the database  
#  save db url at .env for production
engine = create_engine("postgresql://postgres:admin@localhost/testdb")

# Create a session to interact with the database
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the table if it doesn't exist
Base.metadata.create_all(bind=engine)

def get_db():
    database = session_local()
    try:
        yield database
    finally:
        database.close()

db_dependency = Annotated[Session, Depends(get_db)]