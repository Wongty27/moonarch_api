import polars as pl
from app.dependencies.db import db_dependency
from app.dependencies.db import engine
from models.items import Item
from fastapi import APIRouter, HTTPException, Response

router = APIRouter()

# upload new items
@router.post(path="/")
async def create_item(db: db_dependency, filename: str, table_name: str, engine: str):
    db.query(Item).filter()
    df = pl.read_csv(filename)
    df.write_database(table_name=table_name, connection=engine, if_table_exists='append')

# get available items's details
@router.get(path="/")
async def get_item(db: db_dependency):
    pass

# for removing discontinued items
@router.delete(path="/")
async def delete_item(db: db_dependency):
    pass

# for changing stock quantity, price
@router.put(path="/")
async def update_item(db: db_dependency):
    pass