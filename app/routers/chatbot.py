import os
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from app.services.normalbot import call_model

load_dotenv("app/.env")
router = APIRouter()

@router.get("/")
async def ask_question(question: str):
    output = call_model(question=question)
    
    if not output:
        raise HTTPException(status_code=404, detail="Chatbot is not working.")
    
    return output