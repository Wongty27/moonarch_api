from fastapi import APIRouter, Depends, HTTPException
from typing import List, Annotated
from sqlalchemy.orm import Session, joinedload

from models import CartItems, PrebuiltPCs, Products
from schemas import  SimpleResponse, CartResponse, CartItemCreate
from auth import current_user_dependency
from database import db_dependency

router = APIRouter(prefix="/cart", tags=["Cart"])

@router.get("/", response_model=CartResponse)
async def get_cart(
    current_user: current_user_dependency,
    db: db_dependency
):
    cart_items = db.query(CartItems)\
        .options(
            joinedload(CartItems.product_relate),
            joinedload(CartItems.build_relate)
        )\
        .filter(CartItems.user_id == current_user["id"])\
        .all()

    items = []
    for item in cart_items:
        item_data = {
            "cart_item_id": item.cart_item_id,
            "quantity": item.quantity,
            "type": "product" if item.product_id else "prebuilt",
        }

        if item.product_id and item.product_relate:
            item_data.update({
                "item_id": item.product_id,
                "product_name": item.product_relate.product_name,
                "category": item.product_relate.category,
                "price": float(item.product_relate.sales_price),
                "total_price": float(item.product_relate.sales_price * item.quantity),
                "img_url": item.product_relate.img_url
            })
        
        elif item.build_id and item.build_relate:
            item_data.update({
                "item_id": item.build_id,
                "product_name": item.build_relate.build_name,
                "category": "Prebuilt PC",
                "price": float(item.build_relate.build_price),
                "total_price": float(item.build_relate.build_price * item.quantity),
                "img_url": item.build_relate.build_img_url
            })

        items.append(item_data)

    return CartResponse(
        user_id=current_user["id"],
        items=items,
        total_items=sum(item["quantity"] for item in items),
        cart_total=sum(item["total_price"] for item in items)
    )

@router.post("/", response_model=SimpleResponse,description="Add item to cart. Provide either product_id or build_id, not both.")
async def add_to_cart(item: CartItemCreate,current_user: current_user_dependency,db: db_dependency):
    """Add an item to the cart."""
    try:
        # Validate product/build exists
        if item.product_id:
            product = db.query(Products).filter(
                Products.product_id == item.product_id
            ).first()
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
                
            # Check if product already in cart
            existing_item = db.query(CartItems).filter(
                CartItems.user_id == current_user["id"],
                CartItems.product_id == item.product_id
            ).first()

        elif item.build_id:
            build = db.query(PrebuiltPCs).filter(
                PrebuiltPCs.build_id == item.build_id
            ).first()
            if not build:
                raise HTTPException(status_code=404, detail="Prebuilt PC not found")
                
            # Check if build already in cart
            existing_item = db.query(CartItems).filter(
                CartItems.user_id == current_user["id"],
                CartItems.build_id == item.build_id
            ).first()

        if existing_item:
            existing_item.quantity += item.quantity
            db.commit()
            return existing_item

        # Create new cart item
        new_item = CartItems(
            user_id=current_user["id"],
            product_id=item.product_id,
            build_id=item.build_id,
            quantity=item.quantity
        )
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        
        return SimpleResponse(message="Item added to cart successfully")
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bulk", response_model=SimpleResponse)
async def add_bulk_to_cart(
    items: List[CartItemCreate],  # Changed from CartBulkCreate to List[CartItemCreate]
    current_user: current_user_dependency,
    db: db_dependency
):
    """Add multiple items to cart in a single transaction."""
    try:        
        for item in items:  # Directly iterate over the list
            if item.product_id:
                # Validate product exists
                product = db.query(Products).filter(Products.product_id == item.product_id).first()
                if not product:
                    raise HTTPException(
                        status_code=404, 
                        detail=f"Product {item.product_id} not found"
                    )
                
                # Check if product already in cart
                existing_item = db.query(CartItems).filter(
                    CartItems.user_id == current_user["id"],
                    CartItems.product_id == item.product_id
                ).first()

                if existing_item:
                    existing_item.quantity += item.quantity
                else:
                    new_item = CartItems(
                        user_id=current_user["id"],
                        product_id=item.product_id,
                        quantity=item.quantity
                    )
                    db.add(new_item)
                    db.flush()
        db.commit()

        return SimpleResponse(message="Multiple items added to cart successfully")
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/item/{cart_item_id}",response_model=SimpleResponse)
async def update_cart_item(
    cart_item_id: int,
    quantity: int,
    current_user: current_user_dependency,
    db: db_dependency
):
    """Update cart item quantity or remove if quantity is 0"""
    cart_item = db.query(CartItems).filter(
        CartItems.cart_item_id == cart_item_id,
        CartItems.user_id == current_user["id"]  # Ensure user owns this item
    ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    if quantity <= 0:
        # Remove item if quantity is 0 or negative
        db.delete(cart_item)
        db.commit()
        return SimpleResponse(message=f"Item {cart_item_id} removed from cart")
    else:
        # Update quantity
        cart_item.quantity = quantity
        db.commit()
        return SimpleResponse(message=f"Item {cart_item_id} quantity updated")

@router.delete("/",response_model=SimpleResponse)
async def clear_cart(current_user: current_user_dependency,db: db_dependency):
    """Clear all items from user's cart"""
    result = db.query(CartItems).filter(
        CartItems.user_id == current_user["id"]
    ).delete()
    
    db.commit()
    
    if result == 0:
        return SimpleResponse(message="Cart is already empty")
    
    return SimpleResponse(message=f"Cart cleared successfully. {result} items removed")

@router.delete("/item/{cart_item_id}",response_model=SimpleResponse)
async def delete_cart_item(
    cart_item_id: int,
    current_user: current_user_dependency,  
    db: db_dependency
):
    """Delete a specific item from cart"""
    cart_item = db.query(CartItems).filter(
        CartItems.cart_item_id == cart_item_id,
        CartItems.user_id == current_user["id"]  # Ensure user owns this item
    ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    db.delete(cart_item)
    db.commit()
    
    return SimpleResponse(message=f"Item {cart_item_id} removed from cart")
