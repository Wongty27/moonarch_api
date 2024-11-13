from fastapi import APIRouter, Depends, Path, HTTPException
import models
from models import Products,OrderDetails,OrderItems,Feedbacks,Traffics,PrebuiltPCs,PrebuiltOrderItems
from database import engine, SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from datetime import date
from sqlalchemy import func, asc, literal_column, union_all
from auth import get_db, master_required, db_dependency

models.Base.metadata.create_all(bind=engine)

# Assuming master_required is a dependency function that restricts access
dashboard_router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
    dependencies=[Depends(master_required)]  # All routes require 'master' access
)

# Root endpoint for "/dashboard" to serve as a general overview
@dashboard_router.get("/")
async def get_dashboard_overview():
    return {"message": "Welcome to the Business Dashboard"}

@dashboard_router.get("/profits")
async def read_sales(db: db_dependency):
    # First CTE for regular products
    products_cte = (
        db.query(
            OrderDetails.order_id,
            OrderDetails.order_time.label('order_time'),  # Explicitly label
            (func.sum(OrderItems.quantity * Products.cost)).label('order_cost'),
            (func.sum(OrderItems.quantity * Products.sales_price)).label('order_sales_price')
        )
        .join(OrderItems, OrderDetails.order_id == OrderItems.order_id)
        .join(Products, OrderItems.product_id == Products.product_id)
        .group_by(OrderDetails.order_id, OrderDetails.order_time)  # Include order_time in group by
    )

    # Second CTE for prebuilt PCs
    prebuilt_cte = (
        db.query(
            OrderDetails.order_id,
            OrderDetails.order_time.label('order_time'),  # Explicitly label
            (func.sum(PrebuiltOrderItems.quantity * PrebuiltPCs.build_cost)).label('order_cost'),
            (func.sum(PrebuiltOrderItems.quantity * PrebuiltPCs.build_price)).label('order_sales_price')
        )
        .join(PrebuiltOrderItems, OrderDetails.order_id == PrebuiltOrderItems.order_id)
        .join(PrebuiltPCs, PrebuiltOrderItems.build_id == PrebuiltPCs.build_id)
        .group_by(OrderDetails.order_id, OrderDetails.order_time)  # Include order_time in group by
    )

    # Combine both CTEs
    combined_cte = products_cte.union_all(prebuilt_cte).cte('combined_cte')

    # Main query using the combined CTE
    final_query = (
        db.query(
            func.date_trunc('month', combined_cte.c.order_time).label('month'),
            func.sum(combined_cte.c.order_cost).label('total_order_cost'),
            func.sum(combined_cte.c.order_sales_price).label('total_sales_price')
        )
        .group_by('month')
        .order_by('month')
    )

    results = final_query.all()
    
    # Format the results
    return [
        {
            "order_month": result.month.strftime("%b %Y"),  # Format date as "Mon YYYY"
            "total_order_cost": float(result.total_order_cost or 0),
            "total_sales_price": float(result.total_sales_price or 0)
        }
        for result in results
    ]

@dashboard_router.get("/orders")
async def read_orders(db: db_dependency):
    # Regular products CTE
    products_cte = (
        db.query(
            OrderDetails.order_id,
            (func.sum(OrderItems.quantity * Products.sales_price)).label('order_sales_price')
        )
        .join(OrderItems, OrderDetails.order_id == OrderItems.order_id)
        .join(Products, OrderItems.product_id == Products.product_id)
        .group_by(OrderDetails.order_id)
    )

    # Prebuilt PCs CTE
    prebuilt_cte = (
        db.query(
            OrderDetails.order_id,
            (func.sum(PrebuiltOrderItems.quantity * PrebuiltPCs.build_price)).label('order_sales_price')
        )
        .join(PrebuiltOrderItems, OrderDetails.order_id == PrebuiltOrderItems.order_id)
        .join(PrebuiltPCs, PrebuiltOrderItems.build_id == PrebuiltPCs.build_id)
        .group_by(OrderDetails.order_id)
    )

    # Combine both CTEs
    combined_cte = products_cte.union_all(prebuilt_cte).cte(name='combined_cte')

    result = db.query(func.round(func.sum(combined_cte.c.order_sales_price) / func.count(), 2)).scalar()
    return {"average_order_value": result}

@dashboard_router.get("/conversions")
async def read_conversions(db: db_dependency):
    row_count = db.query(func.count(OrderDetails.order_id)).scalar()
    total_traffic = db.query(func.sum(Traffics.number_of_visits)).scalar()

    result = round(row_count / total_traffic * 100, 2)
    response = {"conversion_rate": result}
    return response

@dashboard_router.get("/ratings")
async def read_ratings(db: db_dependency):
    result = db.query(func.avg(Feedbacks.rating)).scalar()
    result = round(result,2)
    response = {"satisfaction_rating": result}
    return response

@dashboard_router.get("/brands")
async def read_brands(db: db_dependency):
    result = db.query(
        func.trim(Products.brand).label("brand"),  # trim whitespace from brand
        Products.category,
        func.sum(OrderItems.quantity).label("total_quantity")  # sum of quantity
    )\
    .join(Products, OrderItems.product_id == Products.product_id)\
    .group_by(Products.category, func.trim(Products.brand))\
    .order_by(Products.category, func.trim(Products.brand)).all()
    response = [{"brand": brand, "category":category, "count":count} for brand,category,count in result]
    return response

@dashboard_router.get("/prebuilt-sales")
async def read_prebuilt_sales(db: db_dependency):
    result = (
        db.query(
            PrebuiltPCs.build_name,
            func.sum(PrebuiltOrderItems.quantity).label("total_sold")
        )
        .join(
            PrebuiltOrderItems,
            PrebuiltPCs.build_id == PrebuiltOrderItems.build_id
        )
        .group_by(
            PrebuiltPCs.build_id,
            PrebuiltPCs.build_name
        )
        .order_by(func.sum(PrebuiltOrderItems.quantity).desc())  # Order by highest sales
        .all()
    )

    # Format the response
    response = [
        {
            "build_name": build_name,
            "total_sold": total_sold
        }
        for build_name, total_sold in result
    ]

    return response

@dashboard_router.get("/stocks")
async def read_stocks(db: db_dependency):
    # Regular products with low stock
    products_result = db.query(
        Products.product_name.label('product_name'),
        Products.stock_count.label('stock_count')
    ).filter(Products.stock_count < 8)

    # Prebuilt PCs with low stock
    prebuilt_result = db.query(
        PrebuiltPCs.build_name.label('product_name'),
        PrebuiltPCs.build_stock_count.label('stock_count')
    ).filter(PrebuiltPCs.build_stock_count < 8)

    # Combine results and order by stock count
    combined_result = products_result.union_all(prebuilt_result)\
        .order_by('stock_count')\
        .all()

    response = [{"product_name": product_name, "stock_count": stock_count} 
                for product_name, stock_count in combined_result]
    return response

@dashboard_router.get("/traffics")
async def read_traffics(db: db_dependency):
    result = db.query(Traffics.visit_date, Traffics.number_of_visits).all()
    response = [{"visit_date": visit_date, "number_of_visits":number_of_visits} for visit_date, number_of_visits in result]
    return response

@dashboard_router.get("/sources")
async def read_sources(db: db_dependency):
    result = db.query(Feedbacks.platform, func.count(Feedbacks.platform)).group_by(Feedbacks.platform).all()
    response = [{"platform": platform, "platform_count":platform_count} for platform,platform_count in result]
    return response

