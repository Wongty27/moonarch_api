from enum import Enum
from app.db.postgres import db_dependency
from app.models.items import Item
from fastapi import APIRouter, HTTPException

router = APIRouter()

class ItemType(int, Enum):
    cpu = 1
    gpu = 2
    mobo = 3
    case = 4
    fan = 5
    cooler = 6
    ssd = 7
    hdd = 8
    ram = 9
    psu = 10

@router.get(path="/{item_type}")
async def get_item(db: db_dependency, item_type: ItemType):
    match item_type:
        case 1:
            results = db.query(Item).filter(Item.type_id == 1).all()
        case 2:
            results = db.query(Item).filter(Item.type_id == 2).all()
        case 3:
            results = db.query(Item).filter(Item.type_id == 3).all()    
        case 4:
            results = db.query(Item).filter(Item.type_id == 4).all()
        case 5:
            results = db.query(Item).filter(Item.type_id == 5).all()
        case 6:
            results = db.query(Item).filter(Item.type_id == 6).all()
        case 7:
            results = db.query(Item).filter(Item.type_id == 7).all()
        case 8:
            results = db.query(Item).filter(Item.type_id == 8).all()
        case default:
            results = db.query(Item).all()

    if not results:
        raise HTTPException(status_code=404, detail="Items not found.")
        
    return results