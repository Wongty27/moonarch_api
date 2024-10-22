import polars as pl
from app.db.conn import db_dependency, DB_URL
from app.models.items import Item
from fastapi import APIRouter, HTTPException, Response

router = APIRouter()

# upload new items
@router.put(path="/")
async def create_item(db: db_dependency, filename: str, table_name: str):
    df = pl.read_csv(filename)
    df.write_database(table_name="item", connection=DB_URL, if_table_exists='append')

# get available items's details
@router.get(path="/")
async def get_item(db: db_dependency):
    return db.query(Item).all()

@router.delete(path="/")
async def delete_item(db: db_dependency):
    pass

@router.post(path="/")
async def update_item(db: db_dependency):
    pass
