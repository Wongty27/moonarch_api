import os
import json
from dotenv import load_dotenv
from typing import Annotated, Sequence, TypedDict
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, ToolMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph.message import add_messages
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool


load_dotenv("app/.env")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_answer(question: str) -> str:
    pass

tools = [get_answer]
model = ChatGoogleGenerativeAI(model='gemini-1.5-flash', api_key=GEMINI_API_KEY)
graph = create_react_agent(model, tools=tools, state_modifier=)
