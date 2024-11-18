import os
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from app.services.normalbot import retrieve_db
from langchain_community.output_parsers.rail_parser import GuardrailsOutputParser

load_dotenv("app/.env")
router = APIRouter()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

@router.get("/")
async def ask_question(question: str) -> str:
    # verify question

    
    ai_response = (retrieve_db(question=question))["result"]
    GuardrailsOutputParser()
    if not ai_response:
        raise HTTPException(status_code=404, detail="Chatbot might feeling sick.")

    # check if answer is relevant to question


    
    return ai_response