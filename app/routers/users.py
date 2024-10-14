from fastapi import APIRouter, HTTPException
from app.dependencies.db import db_dependency
from app.models.orders import Order, Feedback

router = APIRouter(
    prefix="/user"
)

@router.post("")
async def create_user(db: db_dependency):
    db.query()

