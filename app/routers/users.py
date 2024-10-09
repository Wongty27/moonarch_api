from fastapi import APIRouter, HTTPException
from app.db import db_dependency
from models.purchase import NewOrder

router = APIRouter(
    prefix="/user"
)

@router.post("")
async def create_user(db: db_dependency):
    db.query()

