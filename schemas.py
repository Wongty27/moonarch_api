from pydantic import BaseModel, Field, model_validator
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class SimpleResponse(BaseModel):
    message: str

##login request
class UserRequest(BaseModel):
    email: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "yourpassword123"
            }
        }

##login response
class Token(BaseModel):
    access_token: str
    token_type: str

# Update the ProfileUpdate request
class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    street_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postcode: Optional[str] = None
    country: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "John Doe",
                "phone_number": "0123456789",
                "street_address": "123 Main Street",
                "city": "Georgetown",
                "state": "Penang",
                "postcode": "10350",
                "country": "Malaysia"
                }
            }

##update password request
class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str

    class Config:
        json_schema_extra = {
            "example": {
                "old_password": "currentpassword123",
                "new_password": "newpassword123"
            }
        }

##feedback request
class FeedbackData(BaseModel):
    rating: int = Field(..., ge=1, le=5)  # Rating must be between 1 and 5
    platform: str = Field(..., pattern="^(Facebook|Youtube|Twitter|Instagram|Tiktok)$")

##prebuilt pc response
class PrebuiltPCResponse(BaseModel):
    build_id: int
    build_name: str
    build_parts: dict
    build_price: float
    build_img_url: str | None

    class Config: 
        from_attributes = True # Required for SQLAlchemy integration

class CartItem(BaseModel):
    cart_item_id: int
    type: str = Field(description="Either 'product' or 'prebuilt'")
    item_id: int = Field(description="Either product_id or build_id depending on type")
    product_name: str
    category: str
    quantity: int
    price: float = Field(description="Price per unit")
    total_price: float = Field(description="Total price for quantity")
    img_url: Optional[str] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "cart_item_id": 1,
                "type": "product",
                "item_id": 1,  # This would be product_id in this case
                "product_name": "Gaming Mouse",
                "category": "Peripherals",
                "quantity": 2,
                "price": 59.99,
                "total_price": 119.98,
                "img_url": "https://example.com/image.jpg"
            }
        }

class CartResponse(BaseModel):
    user_id: UUID
    items: List[CartItem]
    total_items: int
    cart_total: float

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "items": [
                    {
                        "cart_item_id": 1,
                        "type": "product",
                        "product_name": "Gaming Mouse",
                        "category": "Peripherals",
                        "quantity": 2,
                        "price": 59.99,
                        "total_price": 119.98,
                        "img_url": "https://example.com/image.jpg"
                    },
                    {
                        "cart_item_id": 2,
                        "type": "prebuilt",
                        "product_name": "Gaming PC Pro",
                        "category": "Prebuilt PC",
                        "quantity": 1,
                        "price": 1999.99,
                        "total_price": 1999.99,
                        "img_url": "https://example.com/pc.jpg"
                    }
                ],
                "total_items": 2,
                "cart_total": 2119.97
            }
        }

##add item to cart request
class CartItemCreate(BaseModel):
    product_id: Optional[int] = Field(
        default=None, 
        description="ID of the product (provide either product_id or build_id, not both)"
    )
    build_id: Optional[int] = Field(
        default=None, 
        description="ID of the prebuilt PC (provide either product_id or build_id, not both)"
    )
    quantity: int = Field(
        default=1, 
        gt=0, 
        description="Quantity to add to cart (minimum 1)"
    )

    @model_validator(mode='before')
    @classmethod
    def check_ids(cls, values):
        product_id = values.get('product_id')
        build_id = values.get('build_id')
        
        # Check if both are None or 0
        if (product_id is None or product_id == 0) and (build_id is None or build_id == 0):
            raise ValueError('Must provide either product_id or build_id')
        
        # Check if both are provided
        if (product_id is not None and product_id != 0) and (build_id is not None and build_id != 0):
            raise ValueError('Cannot provide both product_id and build_id')
        
        # Convert 0 to None for cleaner data
        if product_id == 0:
            values['product_id'] = None
        if build_id == 0:
            values['build_id'] = None
            
        return values

    class Config:
        json_schema_extra = {
            "example": {
                "product_id": 1,
                "build_id": None,
                "quantity": 1
            }
        }

class SessionCreate(BaseModel):
        user_id: Optional[UUID] = None

###pydantic models for order details
class OrderItem(BaseModel):
    product_id: int
    quantity: int

# New model for individual product details
class ProductItem(BaseModel):
    product_id: int
    product_name: str
    product_category: str
    product_price: str  # or Decimal if you want to handle decimals
    product_stock: int
    img_url: str | None = None

# Updated ProductResponse model
class ProductResponse(BaseModel):
    title: str
    image: str
    description: str
    product_list: List[ProductItem]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "title": "CPU (Central Processing Unit)",
                "image": "https://example.com/cpu.jpg",
                "description": "The brain of your computer...",
                "product_list": [
                    {
                        "product_id": 1,
                        "product_name": "Intel Core i7",
                        "product_category": "cpu",
                        "product_price": "299.99",
                        "product_stock": 10,
                        "img_url": "https://example.com/i7.jpg"
                    }
                ]
            }
        }

class PrebuiltItem(BaseModel):
    build_id: int
    quantity: int

class DeliveryInfo(BaseModel):
    street_address: str
    city: str
    state: str
    postcode: str
    country: str = 'Malaysia'

class PaymentInfo(BaseModel):
    payment_method: str
    payment_reference: str
    payment_status: str
    payment_time: datetime

class OrderCreate(BaseModel):
    user_id: str
    order_status: str
    products: List[OrderItem]
    prebuilt_items: List[PrebuiltItem]
    delivery_info: DeliveryInfo
    payment_info: PaymentInfo

# ##edit item in cart response
# class CartItemMessage(BaseModel):
#     message: str
#     item_id: Optional[int] = None
#     quantity: Optional[int] = None

# ##add item to cart response
# class CartAddResponse(BaseModel):
#     cart_item_id: int
#     quantity: int
#     message: str = "Item added to cart successfully"

#     class Config:
#         from_attributes = True

# ##bulk add item to cart request
# class CartBulkCreate(BaseModel):
#     items: List[CartItemCreate]

# # Update the bulk request/response schemas
# class CartBulkItemResponse(BaseModel):
#     cart_item_id: int
#     quantity: int

# class CartBulkAddResponse(BaseModel):
#     message: str
#     items: List[CartBulkItemResponse]

