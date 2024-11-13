from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from models import Users, OrderDetails, OrderItems, Products, Feedbacks
from database import SessionLocal
from typing import Annotated, Optional, List
from sqlalchemy.orm import Session, joinedload
from auth import  bcrypt_context, db_dependency, customer_required, current_user_dependency
from uuid import UUID

router = APIRouter(
    prefix="/user",
    tags=["User Profile"],
    dependencies=[Depends(customer_required)]
)

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None

class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str

class FeedbackData(BaseModel):
    rating: int = Field(..., ge=1, le=5)  # Rating must be between 1 and 5
    platform: str = Field(..., pattern="^(Facebook|Youtube|Twitter|Instagram|Tiktok)$")

@router.get("/orders")
async def get_user_orders(
    db: db_dependency,
    current_user: current_user_dependency,
):
    orders = db.query(OrderDetails).filter(
        OrderDetails.user_id == current_user["id"]
    ).options(
        joinedload(OrderDetails.order_items_relate).joinedload(OrderItems.products_relate),
        joinedload(OrderDetails.feedbacks_relate)  # Add this line to load feedback
    ).all()

    response = []
    for order in orders:
        items = []
        for item in order.order_items_relate:
            items.append({
                "product_name": item.products_relate.product_name,
                "category": item.products_relate.category,
                "quantity": item.quantity,
                "price": float(item.products_relate.sales_price)
            })
        
        # Get feedback if it exists
        feedback = None
        if order.feedbacks_relate:
            # Get the first feedback (assuming one feedback per order)
            feedback_record = order.feedbacks_relate[0]
            feedback = {
                "rating": feedback_record.rating,
                "platform": feedback_record.platform
            }
        
        response.append({
            "order_id": order.order_id,
            "order_time": order.order_time.isoformat(),
            "order_status": order.order_status,
            "items": items,
            "feedback": feedback  # Add feedback to response
        })

    return response

@router.get("/profile") 
async def get_user_profile(
    db: db_dependency,
    current_user: current_user_dependency
):
    user = db.query(Users).filter(Users.user_id == current_user["id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    response = {
        "email": user.email,
        "full_name": user.full_name,
        "phone_number": user.phone_number,
        "address": user.address
    }
    return response

@router.put("/profile")
async def update_user_profile(
    db: db_dependency,
    current_user: current_user_dependency,
    profile_data: ProfileUpdate,
):
    user = db.query(Users).filter(Users.user_id == current_user["id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update other fields if provided
    if profile_data.full_name is not None:
        user.full_name = profile_data.full_name
    if profile_data.phone_number is not None:
        user.phone_number = profile_data.phone_number
    if profile_data.address is not None:
        user.address = profile_data.address

    try:
        db.commit()
        return {"message": "Profile updated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update profile")

@router.put("/change-password")
async def change_password(
    db: db_dependency,
    current_user: current_user_dependency,
    password_data: PasswordUpdate
):
    user = db.query(Users).filter(Users.user_id == current_user["id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify old password
    if not bcrypt_context.verify(password_data.old_password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect password")

    # Update password
    user.password = bcrypt_context.hash(password_data.new_password)

    try:
        db.commit()
        return {"message": "Password updated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update password")

@router.post("/orders/feedback/{order_id}")
async def create_feedback(
    order_id: UUID,
    feedback: FeedbackData,
    db: db_dependency,
    current_user: current_user_dependency
):
    # Check if order exists and belongs to current user
    order = db.query(OrderDetails).filter(
        OrderDetails.order_id == order_id,
        OrderDetails.user_id == current_user["id"]
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found or does not belong to current user"
        )

    # Check if order is completed
    if order.order_status != "Completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only provide feedback for completed orders"
        )

    # Check if feedback already exists
    existing_feedback = db.query(Feedbacks).filter(
        Feedbacks.order_id == order_id
    ).first()
    
    if existing_feedback:
        print(existing_feedback)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Feedback already exists for this order"
        )

    # Create new feedback
    try:
        new_feedback = Feedbacks(
            order_id=order_id,
            rating=feedback.rating,
            platform=feedback.platform
        )
        
        db.add(new_feedback)
        db.commit()
        db.refresh(new_feedback)

        return {
            "message": "Feedback submitted successfully",
            "feedback": {
                "rating": new_feedback.rating,
                "platform": new_feedback.platform
            }
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit feedback"
        )