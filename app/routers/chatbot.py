import os
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from app.services.normalbot import retrieve_db, csv_agent, db_agent

load_dotenv("app/.env")
router = APIRouter()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

@router.get("/")
async def ask_question(question: str) -> str:    
    # ai_response = retrieve_db(question=question)
    
    ai_response = db_agent(question)
    
    if not ai_response:
        raise HTTPException(status_code=404, detail="Chatbot might feeling sick.")
    
    return ai_response