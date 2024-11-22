from fastapi import FastAPI
from database import engine
from fastapi.middleware.cors import CORSMiddleware

import models, auth, dashboard, user_profile, build, cart, orders, products
    
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