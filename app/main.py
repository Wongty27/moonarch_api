from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from db import db_dependency
from routers import auth, users, items, purchases

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
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router)
app.include_router(items.router)
app.include_router(purchases.router)


@app.get("/")
async def read_root():
    return "Server is running."