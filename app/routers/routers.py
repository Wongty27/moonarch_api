from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Depends
from sqlalchemy.orm import Session
from db import get_db

router = APIRouter(prefix="/items")

@router.get("")

@router.get("/{item_id}")
async def read_item(item_id: int, request: Request, db: Session = Depends(get_db)) -> Item:
    """_summary_

    Args:
        item_id (int): _description_
        request (Request): _description_
        db (Session, optional): _description_. Defaults to Depends(get_db).

    Raises:
        HTTPException: _description_

    Returns:
        Item: _description_
    """
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