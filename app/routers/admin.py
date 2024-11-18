from fastapi import APIRouter, HTTPException
from app.db.postgres import db_dependency

router = APIRouter()

@router.post("")
async def login(db: db_dependency):
    db.query()

