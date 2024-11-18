from fastapi import APIRouter, HTTPException
from decimal import Decimal
from datetime import datetime
import uuid

from models import CartItems, OrderDetails, OrderItems, Products, PrebuiltPCs, PrebuiltOrderItems, OrderDeliveryInfo, OrderPaymentInfo
from auth import current_user_dependency
from database import db_dependency
from schemas import OrderCreate  # Import from your schemas.py
from pydantic import ValidationError  # Add this import

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/create")
async def create_order(
    order: OrderCreate,
    current_user: current_user_dependency,
    db: db_dependency
):
    """Create order with validation of both token and provided user_id"""
    try:
        print("Received order data:", order.dict())  # Debug log

        # Validate user_id matches the authenticated user
        if str(order.user_id) != current_user["id"]:
            raise HTTPException(
                status_code=403, 
                detail="User ID mismatch with authenticated user"
            )

        # Start transaction
        new_order = OrderDetails(
            order_id=uuid.uuid4(),
            order_time=datetime.now(),
            order_status=order.order_status,
            user_id=current_user["id"]
        )
        db.add(new_order)
        db.flush()

        # Create order items for products
        for item in order.products:
            # Validate product exists and has enough stock
            product = db.query(Products).filter(
                Products.product_id == item.product_id
            ).first()
            if not product:
                raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
            if product.stock_count < item.quantity:
                raise HTTPException(status_code=400, detail=f"Insufficient stock for product {item.product_id}")
            
            # Create order item and update stock
            order_item = OrderItems(
                order_id=new_order.order_id,
                product_id=item.product_id,
                quantity=item.quantity
            )
            db.add(order_item)
            product.stock_count -= item.quantity

        # Create order items for prebuilt PCs
        for item in order.prebuilt_items:
            # Validate prebuilt exists and has enough stock
            build = db.query(PrebuiltPCs).filter(
                PrebuiltPCs.build_id == item.build_id
            ).first()
            if not build:
                raise HTTPException(status_code=404, detail=f"Prebuilt PC {item.build_id} not found")
            if build.build_stock_count < item.quantity:
                raise HTTPException(status_code=400, detail=f"Insufficient stock for prebuilt PC {item.build_id}")
            
            # Create order item and update stock
            prebuilt_order_item = PrebuiltOrderItems(
                order_id=new_order.order_id,
                build_id=item.build_id,
                quantity=item.quantity
            )
            db.add(prebuilt_order_item)
            build.build_stock_count -= item.quantity

        # Create delivery info
        delivery_info = OrderDeliveryInfo(
            order_id=new_order.order_id,
            **order.delivery_info.dict()
        )
        db.add(delivery_info)

        # Create payment info
        payment_info = OrderPaymentInfo(
            order_id=new_order.order_id,
            **order.payment_info.dict()
        )
        db.add(payment_info)

        # Clear cart
        db.query(CartItems).filter(
            CartItems.user_id == current_user["id"]
        ).delete()

        db.commit()

        return {
            "order_id": new_order.order_id,
            "status": "success",
            "message": "Order created successfully"
        }

    except ValidationError as e:
        print("Validation error:", e.errors())  # Debug log
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        print("Error creating order:", str(e))  # Debug log
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{order_id}")
async def get_order(
    order_id: uuid.UUID,
    current_user: current_user_dependency,
    db: db_dependency
):
    """Get order details with both product and prebuilt items"""
    order = db.query(OrderDetails).filter(
        OrderDetails.order_id == order_id,
        OrderDetails.user_id == current_user["id"]
    ).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Get product items
    product_items = db.query(OrderItems).filter(
        OrderItems.order_id == order_id
    ).all()

    # Get prebuilt items
    prebuilt_items = db.query(PrebuiltOrderItems).filter(
        PrebuiltOrderItems.order_id == order_id
    ).all()

    return {
        "order_id": order.order_id,
        "order_time": order.order_time,
        "order_status": order.order_status,
        "product_items": [
            {
                "product_id": item.product_id,
                "quantity": item.quantity,
                "product_name": item.products_relate.product_name,
                "price": float(item.products_relate.sales_price)
            } for item in product_items
        ],
        "prebuilt_items": [
            {
                "build_id": item.build_id,
                "quantity": item.quantity,
                "build_name": item.prebuilt_relate.build_name,
                "price": float(item.prebuilt_relate.build_price)
            } for item in prebuilt_items
        ]
    }