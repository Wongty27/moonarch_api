from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import joinedload

from models import CartItems, PrebuiltPCs, Products
from schemas import  CartResponse, CartItemCreate, SimpleResponse
from auth import current_user_dependency
from main import db_dependency
from typing import List

from fastapi import status
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter(prefix="/cart", tags=["Cart"])

@router.get("/", response_model=CartResponse)
async def get_cart(
    current_user: current_user_dependency,
    db: db_dependency
):
    try:
        # Query cart items with error handling
        try:
            cart_items = db.query(CartItems)\
                .options(
                    joinedload(CartItems.product_relate),
                    joinedload(CartItems.build_relate)
                )\
                .filter(CartItems.user_id == current_user["id"])\
                .all()
        except SQLAlchemyError as db_error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(db_error)}"
            )

        # Process cart items
        try:
            items = []
            for item in cart_items:
                item_data = {
                    "cart_item_id": item.cart_item_id,
                    "quantity": item.quantity,
                    "type": "product" if item.product_id else "prebuilt",
                }

                # Handle product items
                if item.product_id and item.product_relate:
                    item_data.update({
                        "item_id": item.product_id,
                        "product_name": item.product_relate.product_name,
                        "category": item.product_relate.category,
                        "price": float(item.product_relate.sales_price),
                        "total_price": float(item.product_relate.sales_price * item.quantity),
                        "img_url": item.product_relate.img_url
                    })
                
                # Handle prebuilt items
                elif item.build_id and item.build_relate:
                    item_data.update({
                        "item_id": item.build_id,
                        "product_name": item.build_relate.build_name,
                        "category": "Prebuilt PC",
                        "price": float(item.build_relate.build_price),
                        "total_price": float(item.build_relate.build_price * item.quantity),
                        "img_url": item.build_relate.build_img_url
                    })
                else:
                    # Skip invalid items
                    print(f"Warning: Invalid cart item found (ID: {item.cart_item_id})")
                    continue

                items.append(item_data)

            # Calculate totals
            try:
                total_items = sum(item["quantity"] for item in items)
                cart_total = sum(item["total_price"] for item in items)
            except Exception as calc_error:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error calculating cart totals: {str(calc_error)}"
                )

            return CartResponse(
                user_id=current_user["id"],
                items=items,
                total_items=total_items,
                cart_total=cart_total
            )

        except Exception as process_error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing cart items: {str(process_error)}"
            )

    except HTTPException as http_error:
        # Re-raise HTTP exceptions
        raise http_error
    
    except Exception as e:
        # Handle any unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error retrieving cart: {str(e)}"
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
            return SimpleResponse(
                message=f"Item quantity updated to {existing_item.quantity}"
            )

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
        
        return SimpleResponse(
            message="Item added to cart"
    )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/bulk", response_model=SimpleResponse)
async def add_bulk_to_cart(
    items: List[CartItemCreate],
    current_user: current_user_dependency,
    db: db_dependency
):
    """Add multiple items to cart at once."""
    try:
        items_added = 0
        items_updated = 0

        for item in items:
            try:
                # Validate product/build exists
                if item.product_id:
                    product = db.query(Products).filter(
                        Products.product_id == item.product_id
                    ).first()
                    if not product:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Product with ID {item.product_id} not found"
                        )
                    
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
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Prebuilt PC with ID {item.build_id} not found"
                        )
                    
                    # Check if build already in cart
                    existing_item = db.query(CartItems).filter(
                        CartItems.user_id == current_user["id"],
                        CartItems.build_id == item.build_id
                    ).first()

                if existing_item:
                    existing_item.quantity += item.quantity
                    items_updated += 1
                else:
                    # Create new cart item
                    new_item = CartItems(
                        user_id=current_user["id"],
                        product_id=item.product_id,
                        build_id=item.build_id,
                        quantity=item.quantity
                    )
                    db.add(new_item)
                    items_added += 1

            except HTTPException as item_error:
                db.rollback()
                raise item_error

        db.commit()
        
        # Create detailed success message
        message = []
        if items_added > 0:
            message.append(f"{items_added} new item(s) added")
        if items_updated > 0:
            message.append(f"{items_updated} item(s) updated")
            
        return SimpleResponse(
            message=f"Cart updated successfully: {', '.join(message)}"
        )

    except SQLAlchemyError as db_error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(db_error)}"
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )

@router.put("/item/{cart_item_id}", response_model=SimpleResponse)
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
        return SimpleResponse(message="Item removed from cart")
    else:
        # Update quantity
        cart_item.quantity = quantity
        db.commit()
        return SimpleResponse(message="Item quantity updated")

@router.delete("/", response_model=SimpleResponse)
async def clear_cart(current_user: current_user_dependency, db: db_dependency):
    """Clear all items from user's cart"""
    try:
        # Attempt to delete all cart items for the user
        try:
            result = db.query(CartItems).filter(
                CartItems.user_id == current_user["id"]
            ).delete()
            db.commit()
            
        except SQLAlchemyError as db_error:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error while clearing cart: {str(db_error)}"
            )
        
        # Return success message regardless of whether items were deleted
        if result > 0:
            return SimpleResponse(
                message=f"Cart cleared successfully. {result} items removed"
            )
        else:
            return SimpleResponse(
                message="Cart is already empty"
            )
        
    except HTTPException as http_error:
        # Re-raise HTTP exceptions
        raise http_error
    
    except Exception as e:
        # Handle any unexpected errors
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error while clearing cart: {str(e)}"
        )

@router.delete("/item/{cart_item_id}", response_model=SimpleResponse)
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
