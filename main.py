from fastapi import FastAPI
from app.db.postgres import engine
from fastapi.middleware.cors import CORSMiddleware

import app.models as models
import app.routers.auth as auth
import app.routers.dashboard as dashboard
import app.routers.user_profile as user_profile
import app.routers.build as build
import app.routers.cart as cart
import app.routers.orders as orders
import app.routers.products as products
import app.routers.chatbot as chatbot

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(user_profile.router)
app.include_router(products.router)
app.include_router(build.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(dashboard.dashboard_router)
app.include_router(chatbot.router)