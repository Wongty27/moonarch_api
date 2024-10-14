from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.routers import orders
from app.dependencies.db import db_dependency
from routers import auth, users, items, info

app = FastAPI(
    # dependencies=db_dependency,
)

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include dependencies
app.include_router(info.router, prefix="/info", tags=["info"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router,  prefix="/users", tags=["users"])
app.include_router(items.router, prefix="/items", tags=["items"])
app.include_router(orders.router, prefix="/orders", tags=["orders"])



@app.get("/")
async def read_root():
    return "Server is running."