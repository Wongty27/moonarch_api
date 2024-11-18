from typing import Annotated
from sqlalchemy import and_, or_
from app.db.postgres import db_dependency
from app.models.items import Item
from fastapi import APIRouter, HTTPException, Response, Query
from app.models.orders import OrderModel, FeedbackModel
from app.schemas.orders import OrderSchema, FeedbackSchema

router = APIRouter()

@router.post("/")
async def create_order(db: db_dependency, new_order: OrderSchema):
    return new_order

@router.get("/", response_model=OrderSchema)
async def get_order(
    db: db_dependency,
    customer_email: Annotated[str | None, Query(min_length=10, max_length=50, pattern="^@")] = None,
    order_id: int | None = None,
    status: str | None = None,
):
    if customer_email and order_id:
        results = db.query(OrderModel).filter(and_(OrderModel.customer_email == customer_email, OrderModel.id == order_id, OrderModel.status == status)).all()
    elif customer_email or order_id or status:
        results = db.query(OrderModel).filter(or_(OrderModel.customer_email == customer_email, OrderModel.id == order_id, OrderModel.status == status)).all()
    else:
        results = db.query(OrderModel).all()

    if not results:
        raise HTTPException(status_code=404, detail="Order not found.")

    return results

@router.put("/", response_model=OrderSchema)
async def update_order(
    db: db_dependency,
    customer_email: str | None = None,
    order_id: int | None = None,
    status: str | None = None,
):
    if customer_email and order_id:
        results = db.query(OrderModel).filter(and_(OrderModel.customer_email == customer_email, OrderModel.id == order_id, OrderModel.status == status)).all()
    elif customer_email or order_id or status:
        results = db.query(OrderModel).filter(or_(OrderModel.customer_email == customer_email, OrderModel.id == order_id, OrderModel.status == status)).all()
    else:
        results = db.query(OrderModel).all()

    if not results:
        raise HTTPException(status_code=404, detail="Order not found.")

    return results