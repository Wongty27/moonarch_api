from database import Base
from sqlalchemy import Column, Integer, String, Date, Numeric, Text, TIMESTAMP, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

##define product as class
class Products(Base):
    __tablename__ = "products"  # Table name in the database

    product_id = Column(Integer, primary_key=True, autoincrement=True)  # Primary key with auto increment
    product_name = Column(String(255), nullable=False)  # Product name, not null
    brand = Column(String(100), nullable=False)  # Brand name, not null
    category = Column(String(100), nullable=False)  # Category, not null
    cost = Column(Numeric(10, 2), nullable=False)  # Cost with two decimal places
    sales_price = Column(Numeric(10, 2), nullable=False)  # Sales price with two decimal places
    stock_count = Column(Integer, nullable=False)  # Quantity, not null

    # relationship
    order_items_relate = relationship("OrderItems", back_populates="products_relate")

class Users(Base):
    __tablename__ = 'users'  # Table name should match your PostgreSQL table

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # UUID as primary key
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    phone_number = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    user_type = Column(String(50), nullable=False)

    # relationship
    order_details_relate = relationship("OrderDetails", back_populates="users_relate")  # Correlates to the 'user' in OrderDetails

class OrderDetails(Base):
    __tablename__ = 'order_details'  # Name of the table in the database

    order_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # UUID as primary key with default value
    order_time = Column(TIMESTAMP, nullable=False)  # Timestamp for the order time
    order_status = Column(String(50), nullable=False)  # Varchar for order status with a max length of 50
    user_id = Column(UUID, ForeignKey('users.user_id'), nullable=False)  # Foreign key referencing users table

    # Optionally, define a relationship to the User model
    users_relate = relationship("Users", back_populates="order_details_relate")
    feedbacks_relate = relationship("Feedbacks", back_populates="order_details_relate")
    order_items_relate = relationship("OrderItems", back_populates="order_details_relate")
    prebuilt_order_items_relate = relationship("PrebuiltOrderItems", back_populates="order_details_relate")  # New relationship


class OrderItems(Base):
    __tablename__ = 'order_items'

    order_id = Column(UUID, ForeignKey('order_details.order_id', ondelete='CASCADE'), primary_key=True)
    product_id = Column(Integer, ForeignKey('products.product_id', ondelete='CASCADE'), primary_key=True)
    quantity = Column(Integer, nullable=False)

    # Define relationships
    order_details_relate = relationship("OrderDetails", back_populates="order_items_relate")
    products_relate = relationship("Products", back_populates="order_items_relate")

class Feedbacks(Base):
    __tablename__ = 'feedbacks'

    order_id = Column(UUID, ForeignKey('order_details.order_id', ondelete='CASCADE'), primary_key=True)
    rating = Column(Integer, CheckConstraint('rating >= 1 AND rating <= 5'), nullable=False)
    platform = Column(String(255), nullable=False)

    # Define relationship
    order_details_relate = relationship("OrderDetails", back_populates="feedbacks_relate")

class Traffics(Base):
    __tablename__ = "traffics"  # Table name in the database

    traffic_id = Column(Integer, primary_key=True, autoincrement=True)  # Unique ID for each traffic record
    visit_date = Column(Date, nullable=False)  # Date of the traffic record
    number_of_visits = Column(Integer, nullable=False)  # Number of visits for that day

class PrebuiltPCs(Base):
    __tablename__ = "prebuilt"

    build_id = Column(Integer, primary_key=True)
    build_name = Column(String(255), nullable=False)
    build_parts = Column(JSONB, nullable=True)
    build_img_url = Column(String(255), nullable=True)
    build_cost = Column(Numeric(10, 2), nullable=False)
    build_price = Column(Numeric(10, 2), nullable=False)
    build_stock_count = Column(Integer, nullable=False)

    # relationship
    prebuilt_order_items_relate = relationship("PrebuiltOrderItems", back_populates="prebuilt_relate")

class PrebuiltOrderItems(Base):
    __tablename__ = 'prebuilt_order_items'

    order_id = Column(UUID, ForeignKey('order_details.order_id', ondelete='CASCADE'), primary_key=True)
    build_id = Column(Integer, ForeignKey('prebuilt.build_id', ondelete='CASCADE'), primary_key=True)
    quantity = Column(Integer, nullable=False)

    # Define relationships
    order_details_relate = relationship("OrderDetails", back_populates="prebuilt_order_items_relate")
    prebuilt_relate = relationship("PrebuiltPCs", back_populates="prebuilt_order_items_relate")