from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.params import Depends
from sqlalchemy.orm import Session
from models.items import ItemMaster
from app.dependencies.db import get_db

router = APIRouter()

@router.get("/{item_id}")
async def read_item(item_id: int, request: Request) -> Item:
    try:
        db_item = read_db_item()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404) from e
    return Item(**db_item.__dict__)

@router.post("/{item_id}")
async def create_item():
    pass

@router.put("/{item_id}")
async def update_item():
    pass 

@router.delete("/{item_id}")
async def delete_item():
    pass