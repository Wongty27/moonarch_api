import pandas as pd
from app.dependencies.db import db_dependency
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.items import Item
from pydantic import DirectoryPath
from fastapi import APIRouter, HTTPException, Response

router = APIRouter()

@router.post("")
async def upload_data(db: db_dependency, filename: str, table_name: str, engine: str):
    db.query(Item).filter()
    df = pd.read_csv(filename)
    df.to_sql(name=table_name, con=engine, if_exists='append', index=False)
