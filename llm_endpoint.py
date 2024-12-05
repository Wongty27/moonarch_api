import os
from typing import Annotated, Dict, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import Tool, AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import BaseTool, StructuredTool, tool
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage
from dotenv import load_dotenv
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from datetime import datetime
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate


from google.cloud import aiplatform
from langchain_google_vertexai import ChatVertexAI


from models import Time, Doctors
from database import SessionLocal
from tools.book_appointment import book_appointment, BookingRequest, confirm_booking, book_appointments, MultipleBookingRequest
from tools.date_tools import get_today_date, get_future_date
from tools.hospital_info import get_doctor, get_doctors, get_doctor_availability, doctorToJson, get_doctors_availability, MultipleCheck
from tools.vector_tools import get_mongo_db

load_dotenv()

router = APIRouter()

# Environment variables:
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
GCP_LOCATION = os.environ.get("GCP_LOCATION")
MONGODB_ATLAS_CLUSTER_URI = os.environ.get("MONGODB_ATLAS_CLUSTER_URI")

# Initialize Vertex AI:
try:
    aiplatform.init(project=GCP_PROJECT_ID, location=GCP_LOCATION)
    print("Vertex AI initialized successfully.")
except Exception as e:
    print(f"An error occurred while initializing Vertex AI: {e}")
    raise

# Initialize conversation memory
conversation_memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

# Initialize the language model with the API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# llm = ChatGoogleGenerativeAI(
#     model='gemini-1.5-flash-latest',
#     temperature=0,
#     api_key=GEMINI_API_KEY
# )
llm = ChatVertexAI(
    model="gemini-1.5-pro",
    temperature=0,
)

@tool
def addition_tool(input_string: str) -> str:
    """Performs addition of two numbers."""
    try:
        a, b = map(float, input_string.split(','))
        return f"The sum of {a} and {b} is {a + b}"
    except ValueError:
        return "Error: Please provide two valid numbers separated by a comma."
    
@tool
def easter_egg(input_string: str) -> str:
    """Secret easter egg function."""
    return "Congratulations! You've found the secret easter egg. Here's a virtual cookie: 🍪"

# Initialize tools
# TODO: Implement DRY
tools = [
    Tool(
        name="Addition",
        func=addition_tool,
        description="Adds two numbers. Input: two numbers separated by a comma."
    ),
    Tool(
        name="Today_Date",
        func=get_today_date,
        description="Returns today's date in YYYY-MM-DD format. Input: Magic word 'Today'"
    ),
    Tool(
        name="Future_Date",
        func=get_future_date,
        description="Returns dates for 'today', 'tomorrow', or future days using 'next <day_of_week>' format (e.g., 'next thursday'). Days must be spelled in full."
    ),
    Tool(
        name="Doctors",
        func=get_doctors,
        description="Return the collections of doctors. Input: Magic word 'Doctors'"
    ),
    Tool(
        name="Specific_Doctor_Information",
        func=get_doctor,
        description="Retrieves information about a specific doctor, including upcoming appointments. Input: doctor's ID or name."
    ),
    Tool(
        name="Alpha_Hospital_General_Infomation",
        func=get_mongo_db,
        description="Can answer general questions about medical conditions, treatments, healthcare services, and hospital-related inquiries. Input: Any natural language question or query about healthcare, medical topics, or hospital services."
    ),
    Tool(
        name="Check_Doctor_Availability",
        func=get_doctor_availability,
        description="Checks availability for a specific doctor. Input: doctor's name."
    ),
    Tool(
        name="Easter_Egg",
        func=easter_egg,
        description="A secret function that can only be accessed with a special keyword of 'alpha'."
    ),
    StructuredTool.from_function(
        func=get_doctors_availability,
        name="Doctors_Availability",
        description="Checks current availability status of list doctors. Input: A list of doctors name from database.",
        args_schema=MultipleCheck,
        return_direct=True,
    ),
    StructuredTool.from_function(
        func=book_appointment,
        name="Book_Appointment",
        description="""
            Books an appointment with a doctor, phone number must be a valid Malaysian format (+60 or 01x).
            Input: A dictionary with keys 'doctor_name', 'date', 'time', 'patientEmail',
            'patientName', 'phone_number'.
        """,
        args_schema=BookingRequest,
        return_direct=True,
    ),
    StructuredTool.from_function(
        func=confirm_booking,
        name="Confirm_Booking",
        description="Rechecks and confirms if a booking was successful. Input: A dictionary with keys 'doctor_name', 'date', 'time'.",
        args_schema=BookingRequest,
        return_direct=True,
    ),
    # Create the StructuredTool
    StructuredTool.from_function(
        func=book_appointments,
        name="Smart_Booking",
        description="""
            Books an appointment for a single doctor on a specific date with optimized scheduling. 
            This is a special feature triggered by the phrase 'smart booking'.
            Input: A dictionary with keys 'doctor_name', 'date', 'time', and 'duration'
        """,
        args_schema=MultipleBookingRequest,
        return_direct=True,
    )
]

# Create a Pydantic model for the chat request
class ChatRequest(BaseModel):
    question: str
    session_id: str = Field(default=None, description="Unique identifier for the conversation session")

# Create a dictionary to store session-specific memories
session_memories: Dict[str, ConversationBufferMemory] = {}

def get_or_create_memory(session_id: str) -> ConversationBufferMemory:
    """Get or create a memory instance for a specific session."""
    if session_id not in session_memories:
        session_memories[session_id] = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
    return session_memories[session_id]

# First, get the list of doctors from the database
doctors_list = get_doctors.invoke("get list of doctor")

# Create the system prompt with the doctors list
system_message = f"""
    You are a helpful assistant for Alpha Hospital.
    You help patients book appointments, check doctor availability, provide information about doctors and Alpha Hospital.

    Available Doctors in Alpha Hospital Database:
    {doctors_list}

    Current Time: {datetime.now().strftime('%Y-%m-%d %H-%M')}

    Whenever suggesting doctor appointments, MAKE SURE the suggested doctors are in the above Alpha hospital database.
    If patient give a time, directly use 'Doctors' tools to suggest doctors. Make it in markdown format. Make sure the picture format is not empty.
    Whenever patient want hospital list of doctors, the output should be in MARKDOWN format. Make sure the picture format is not empty.
    ALWAYS provide immediate response.

    IMPORTANT: You must ALWAYS use the 'Book_Appointment' tool to actually book an appointment.
    Convert all time inputs to the format 'HH:MM AM/PM'. Ensure appointments are only scheduled between 09:00 AM and 05:00 PM.
    Never claim an appointment has been booked unless you've used this tool and received a 'BOOKING_CONFIRMED' response.
    If asked to book an appointment, always use the tool and report the exact result to the user.
    ALWAYS maintain a professional and caring tone.
    ALWAYS tabulate suggested doctor in table. The table should contain picture, name and specialty.

    If the user has triggered the easter egg 'smart booking', acknowledge it and then ask for a brief health description for each appointment.
    Use this information to determine appropriate appointment durations (30 minutes, 1 hour or 2 hours).
    Before booking, suggest appropriate appointment durations for patient.
"""


# Create prompt template with system message and memory
prompt = ChatPromptTemplate.from_messages([
    ("system", system_message),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# Construct the Tools agent with memory
agent = create_tool_calling_agent(llm.bind_tools(tools), tools, prompt)

def recheck_booking(message: str) -> bool:
    """
    Checks if a message contains a booking that needs to be rechecked.
    Returns True if booking needs verification, False otherwise.
    """
    class ReconfirmAppointment(BaseModel):
        ifBooked: bool = Field(
            description="True if message contains a booking to recheck, False otherwise"
        )

    parser = JsonOutputParser(pydantic_object=ReconfirmAppointment)

    prompt = PromptTemplate(
        template="""
        Determine if this message contains a booking or appointment that needs to be rechecked.
        Return True only if there's a clear mention of a booking or appointment.
        
        Message: {query}
        
        {format_instructions}
        """,
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    try:
        chain = prompt | llm | parser
        result = chain.invoke({"query": message})
        return result["ifBooked"]
    except:
        return False
    


@router.post("/gemini_v0_legacy")
async def tooling(chat_request: ChatRequest):
    if not chat_request.question:
        raise HTTPException(status_code=400, detail="Question parameter is required")

    # Get or create session-specific memory
    memory = get_or_create_memory(chat_request.session_id)

    # Create an agent executor with memory
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True
    )

    try:
        # Get the conversation history
        chat_history = memory.chat_memory.messages if memory.chat_memory.messages else []

        # Execute the agent with the question and memory
        results = agent_executor.invoke({
            "input": f"{chat_request.question}\n RAG Information:{get_mongo_db.invoke(chat_request.question)}",
            "chat_history": chat_history,
        })

        # Clean the response by stripping leading/trailing whitespace and newlines
        cleaned_response = results["output"].strip()

        # specific markdown format
        doctor_json_response = doctorToJson(results["output"])
        if doctor_json_response:
            cleaned_response = doctorToJson(results["output"])

        # Return the results along with the conversation history
        return {
            "gemini_response": cleaned_response,
            "chat_history": [
                {"role": msg.type, "content": msg.content.strip()}
                for msg in memory.chat_memory.messages
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your request: {str(e)}. "
                    "Please try rephrasing your question or contact support if the issue persists."
        )
    

# First, modify the imports and add MongoDBMessageHistory
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from langchain.memory import ConversationBufferMemory

# Remove the old session_memories dictionary and replace with MongoDB connection details
MONGODB_URL = os.getenv("MONGODB_ATLAS_CLUSTER_URI")
DB_NAME = "alpha_hospital_db"
COLLECTION_NAME = "chat_histories"

def get_or_create_memory(session_id: str) -> ConversationBufferMemory:
    """Get or create a memory instance for a specific session using MongoDB."""
    message_history = MongoDBChatMessageHistory(
        connection_string=MONGODB_URL,
        database_name=DB_NAME,
        collection_name=COLLECTION_NAME,
        session_id=session_id,
    )

    return ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        chat_memory=message_history
    )

# originally v0
@router.post("/gemini_v1")
async def tooling(chat_request: ChatRequest):
    if not chat_request.question:
        raise HTTPException(status_code=400, detail="Question parameter is required")

    # Get or create session-specific memory using MongoDB
    memory = get_or_create_memory(chat_request.session_id)

    # Create an agent executor with memory
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True
    )
    agent_no_memory = AgentExecutor(
        agent=agent,
        tools=tools
    )

    try:
        # Get the conversation history
        chat_history = memory.chat_memory.messages if memory.chat_memory.messages else []

        # Execute the agent with the question and memory
        results = agent_executor.invoke({
            "input": f"#Question {chat_request.question}",
            "chat_history": chat_history,
        })

        # Clean the response by stripping leading/trailing whitespace and newlines
        cleaned_response = results["output"].strip()

        # specific markdown format
        doctor_json_response = doctorToJson(results["output"])

        # Recheck
        isBooked = recheck_booking(results["output"])

        # if isBooked:
        #     results = agent_no_memory.invoke({
        #         "input": f"Booked appointment based on this chat history\n\n # Chat History\n\n{chat_history}"
        #     })

        # Filter out RAG-related messages from chat history
        filtered_chat_history = []

        for msg in memory.chat_memory.messages:
            # Skip messages that contain RAG-related content
            if not any(rag_indicator in msg.content.lower() for rag_indicator in 
                      ['retrieved from database', 'search result', 'found in documents',
                       'according to the database', 'based on the retrieved information']):
                filtered_chat_history.append({
                    "role": msg.type,
                    "content": msg.content.strip()
                })
        
        # Return the results along with the filtered conversation history
        return {
            "gemini_response": cleaned_response,
            "chat_history": filtered_chat_history
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your request: {str(e)}. "
                    "Please try rephrasing your question or contact support if the issue persists."
        )
