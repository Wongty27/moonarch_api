from fastapi import FastAPI, Depends
from app.models import main as models
from fastapi.middleware.cors import CORSMiddleware
from app.routers import orders, items
from app.db.main import engine

api = FastAPI(
    # dependencies=db_dependency,
)

models.Base.metadata.create_all(bind=engine)

origins = [
    "http://localhost:3000",
]

api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# api.include_router(info.router, prefix="/info", tags=["info"])
# api.include_router(auth.router, prefix="/auth", tags=["auth"])
# api.include_router(users.router,  prefix="/users", tags=["users"])
api.include_router(items.router, prefix="/items", tags=["items"])
# api.include_router(orders.router, prefix="/orders", tags=["orders"])

@api.get("/")
async def read_root():
    return "Welcome."