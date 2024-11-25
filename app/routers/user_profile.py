from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import joinedload
from uuid import UUID

from app.models import Users, OrderDetails, OrderItems, Feedbacks, PrebuiltOrderItems
from app.schemas import ProfileUpdate, PasswordUpdate, FeedbackData
from app.db.postgres import db_dependency
from app.routers.auth import bcrypt_context, customer_required, current_user_dependency

router = APIRouter(
    prefix="/user",
    tags=["User Profile"],
    dependencies=[Depends(customer_required)]
)

@router.get("/orders")
async def get_user_orders(
    db: db_dependency,
    current_user: current_user_dependency,
):
    orders = db.query(OrderDetails).filter(
        OrderDetails.user_id == current_user["id"]
    ).options(
        joinedload(OrderDetails.order_items_relate).joinedload(OrderItems.products_relate),
        joinedload(OrderDetails.prebuilt_order_items_relate).joinedload(PrebuiltOrderItems.prebuilt_relate),
        joinedload(OrderDetails.feedbacks_relate)
    ).all()

    if not orders:
        raise HTTPException(status_code=404, detail="No orders found")

    response = []

    for order in orders:
        items = []
        
        # Handle regular product items
        for item in order.order_items_relate:
            items.append({
                "product_name": item.products_relate.product_name,
                "category": item.products_relate.category,
                "quantity": item.quantity,
                "price": float(item.products_relate.sales_price),
                "type": "product"  # Add type to distinguish between products and prebuilts
            })
        
        # Handle prebuilt PC items
        for prebuilt_item in order.prebuilt_order_items_relate:
            items.append({
                "product_name": prebuilt_item.prebuilt_relate.build_name,
                "category": "Prebuilt PC",  # Fixed category for prebuilts
                "quantity": prebuilt_item.quantity,
                "price": float(prebuilt_item.prebuilt_relate.build_price),
                "type": "prebuilt"  # Add type to distinguish between products and prebuilts
            })
        
        # Get feedback if it exists
        feedback = None
        if order.feedbacks_relate:
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
            "feedback": feedback
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
        "street_address": user.street_address,
        "city": user.city,
        "state": user.state,
        "postcode": user.postcode,
        "country": user.country
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

    # Update using dict comprehension to handle all fields
    update_data = {
        k: v for k, v in profile_data.dict(exclude_unset=True).items()
        if v is not None
    }
    
    for key, value in update_data.items():
        setattr(user, key, value)

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
    
        # Additional password validation could go here
    if password_data.old_password == password_data.new_password:
        raise HTTPException(
            status_code=400, 
            detail="New password must be different from old password"
        )

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