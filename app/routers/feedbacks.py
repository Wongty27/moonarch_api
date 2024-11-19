from sqlalchemy import and_, or_
from app.db.postgres import db_dependency
from fastapi import APIRouter, HTTPException, Response
from app.models.orders import FeedbackModel
from app.schemas.orders import FeedbackSchema

router = APIRouter()

@router.post("/create_feedback")
async def create_feedback(db: db_dependency, feedback: FeedbackSchema):
    new_feedback = FeedbackModel(**feedback.model_dump())
    db.add(new_feedback)
    db.commit()

@router.get("/get_feedback", response_model=FeedbackSchema)
async def get_feedback(
    db: db_dependency,
    order_id: int | None = None,
    rating: int | None = None,
):
    if order_id and rating:
        results = db.query(FeedbackModel).filter(and_(FeedbackModel.id == order_id, FeedbackModel.rating == rating)).all()
    elif order_id or rating:
        results = db.query(FeedbackModel).filter(or_(FeedbackModel.id == order_id, FeedbackModel.rating == rating)).all()
    else:
        results = db.query(FeedbackModel).all()

    if not results:
        raise HTTPException(status_code=404, detail="Feedback not found.")

    return results