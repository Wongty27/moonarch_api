from fastapi import FastAPI, Depends
from app.models import main as models
from fastapi.middleware.cors import CORSMiddleware
from app.routers import orders, items, feedbacks, chatbot
from app.db.postgres import engine

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

api.include_router(chatbot.router, prefix="/chatbot", tags=["chatbot"])
# api.include_router(auth.router, prefix="/auth", tags=["auth"])
# api.include_router(feedbacks.router,  prefix="/feedbacks", tags=["feedbacks"])
# api.include_router(items.router, prefix="/items", tags=["items"])
# api.include_router(orders.router, prefix="/orders", tags=["orders"])

@api.get("/")
async def read_root():
    return "Welcome."