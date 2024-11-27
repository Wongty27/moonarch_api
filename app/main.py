from fastapi import FastAPI
from db.postgres import engine
from fastapi.middleware.cors import CORSMiddleware

import models as models
import routers.auth as auth
import routers.dashboard as dashboard
import routers.user_profile as user_profile
import routers.build as build
import routers.cart as cart
import routers.orders as orders
import routers.products as products
import routers.chatbot as chatbot

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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