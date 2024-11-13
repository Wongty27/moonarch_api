from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from models import PrebuiltPCs
from database import SessionLocal
from auth import db_dependency

router = APIRouter(prefix="/shop", tags=["Shop"])

# Pydantic model for response
class PrebuiltPCResponse(BaseModel):
    build_id: int
    build_name: str
    build_parts: dict
    build_price: float
    build_img_url: str | None

    class Config: 
        from_attributes = True # Required for SQLAlchemy integration

@router.get("/prebuilt", response_model=List[PrebuiltPCResponse])
async def get_all_prebuilt_pcs(db: db_dependency):
    try:
        prebuilt_pcs = db.query(PrebuiltPCs).all()
        if not prebuilt_pcs:
            raise HTTPException(status_code=404, detail="No prebuilt PCs found")
        return prebuilt_pcs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))