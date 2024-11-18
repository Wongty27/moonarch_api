from fastapi import FastAPI
from database import engine
from fastapi.middleware.cors import CORSMiddleware

import models
import auth
import dashboard
import user_profile
import build
import cart
import orders
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
app.include_router(dashboard.dashboard_router)
app.include_router(user_profile.router)
app.include_router(build.router)
app.include_router(cart.router)
app.include_router(orders.router)
