from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from models import PrebuiltPCs
from database import SessionLocal, db_dependency
from schemas import PrebuiltPCResponse

router = APIRouter(prefix="/shop", tags=["Shop"])

@router.get("/prebuilt", response_model=List[PrebuiltPCResponse])
async def get_all_prebuilt_pcs(db: db_dependency):
    try:
        prebuilt_pcs = db.query(PrebuiltPCs).all()
        if not prebuilt_pcs:
            raise HTTPException(status_code=404, detail="No prebuilt PCs found")
        return prebuilt_pcs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))