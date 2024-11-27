from fastapi import FastAPI, Depends
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from typing import Annotated

from fastapi.middleware.cors import CORSMiddleware

import models
import auth
import dashboard
import user_profile
import build
import cart
import orders
import products
import chatbot

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# db_dependency = Annotated[Session, Depends(get_db)]

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://gaia-capstone08-prd.web.app/",
        "https://gaia-capstone08-prd.firebaseapp.com/",
        "https://moonarch-api-service-220646501559.us-central1.run.app",

    ],
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