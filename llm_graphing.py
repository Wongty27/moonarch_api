# %%
import os
from datetime import date, datetime
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
from langgraph.prebuilt import ToolExecutor, ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_core.messages import AIMessage
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional, List

from models import Time, Doctors
from database import SessionLocal
from tools.book_appointment import book_appointment, BookingRequest, confirm_booking, book_appointments, MultipleBookingRequest
from tools.date_tools import get_today_date, get_future_date
from tools.hospital_info import get_doctor, get_doctors, get_doctor_availability, doctorToJson, get_doctors_availability, MultipleCheck, get_doctors_availability_by_time, DoctorsTimeDateCheck
from tools.vector_tools import get_mongo_db
from langchain_google_vertexai import ChatVertexAI


load_dotenv()

router = APIRouter()

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
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# llm = ChatGoogleGenerativeAI(
#     model='gemini-1.5-flash-latest',
#     temperature=0,
#     api_key=GEMINI_API_KEY
# )

llm = ChatVertexAI(
    model="gemini-1.5-pro",
    temperature=0
)

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

# Define tools
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

@tool
def get_weather(location: str):
    """Call to get the current weather."""
    if location.lower() in ["sf", "san francisco"]:
        return "It's 60 degrees and foggy."
    else:
        return "It's 90 degrees and sunny."

@tool
def get_coolest_cities(input: str):
    """Get a list of coolest cities"""
    return "nyc, sf"

# Define tools list
tools = [
    Tool(name="Addition", func=addition_tool, description="Adds two numbers. Input: two numbers separated by a comma."),
    Tool(name="Today_Date", func=get_today_date, description="Returns today's date in YYYY-MM-DD format. Input: Magic word 'Today'"),
    Tool(name="Future_Date", func=get_future_date, description="Returns the date for a specified day in the future (e.g., 'next thursday', 'next monday'). Input: 'next <day_of_week>'."),
    Tool(name="Doctors", func=get_doctors, description="Return the collections of doctors. Input: Magic word 'Doctors'"),
    Tool(name="Specific_Doctor_Information", func=get_doctor, description="Retrieves information about a specific doctor, including upcoming appointments. Input: doctor's ID or name."),
    Tool(name="Retrieve_Vector_Mongo", func=get_mongo_db, description="Retrieves relevant information about Alpha Hospital from a MongoDB database using vector search. Input: A natural language question or query about Alpha Hospital."),
    Tool(name="Check_Doctor_Availability", func=get_doctor_availability, description="Checks availability for a specific doctor. Input: doctor's name."),
    Tool(name="Easter_Egg", func=easter_egg, description="A secret function that can only be accessed with a special keyword of 'alpha'."),
    StructuredTool.from_function(func=get_doctors_availability, name="Doctors_Availability", description="Checks schedule for multiple doctor if asked by user. Input: A list of doctors name from database.", args_schema=MultipleCheck, return_direct=True),
    StructuredTool.from_function(func=book_appointment, name="Book_Appointment", description="Books an appointment with a doctor, phone number must be a valid Malaysian format (+60 or 01x). Input: A dictionary with keys 'doctor_name', 'date', 'time', 'patientEmail','patientName', 'phone_number'.", args_schema=BookingRequest, return_direct=True),
    StructuredTool.from_function(func=confirm_booking, name="Confirm_Booking", description="Rechecks and confirms if a booking was successful. Input: A dictionary with keys 'doctor_name', 'date', 'time'.", args_schema=BookingRequest, return_direct=True),
    StructuredTool.from_function(func=book_appointments, name="Smart_Booking", description="Books an appointment for a single doctor on a specific date with optimized scheduling. This is a special feature triggered by the phrase 'smart booking'. Input: A dictionary with keys 'doctor_name', 'date', 'time', and 'duration'", args_schema=MultipleBookingRequest, return_direct=True),
    StructuredTool.from_function(
    func=get_doctors_availability_by_time,
    name="Check_Time_Availability",
    description="Checks availability for multiple doctors at a specific time. Input: list of doctor names and a specific time (and optionally a date).",
    args_schema=DoctorsTimeDateCheck,
    return_direct=True
    ),
]

# # Set up the graph
# tool_node = ToolNode(tools)
# llm_with_tools = llm.bind_tools(tools)

# class State(TypedDict):
#     messages: Annotated[list, add_messages]

# def call_model(state: MessagesState):
#     messages = state["messages"]
#     response = llm_with_tools.invoke(messages)
#     return {"messages": [response]}

# def should_continue(state: MessagesState):
#     messages = state["messages"]
#     last_message = messages[-1]
    
#     if isinstance(last_message, AIMessage):
#         # Check if the AI's last message contains tool calls
#         if last_message.tool_calls:
#             return "tools"
        
#         # Check if the AI needs to think more
#         if "I need to think about this" in last_message.content.lower():
#             return "think"
        
#         # If no tool calls and no need to think, end the conversation
#         return END
    
#     # If the last message is not from the AI, continue with the agent
#     return "agent"

# # Add a new node for the 'think' step
# def think(state: MessagesState):
#     messages = state["messages"]
#     think_prompt = "Let's take a moment to reflect on the current state of the conversation and consider if we need any additional information or tools to proceed."
#     response = llm.invoke(messages + [SystemMessage(content=think_prompt)])
#     return {"messages": [response]}

# # Update the workflow
# workflow = StateGraph(MessagesState)
# workflow.add_node("agent", call_model)
# workflow.add_node("tools", tool_node)
# workflow.add_node("think", think)

# workflow.add_edge(START, "agent")
# workflow.add_conditional_edges("agent", should_continue, ["tools", "think", END])
# workflow.add_edge("tools", "agent")
# workflow.add_edge("think", "agent")

# from langgraph.checkpoint.memory import MemorySaver

# memory = MemorySaver()

# graph = workflow.compile(checkpointer=memory)

# from IPython.display import Image, display

# try:
#     display(Image(graph.get_graph().draw_mermaid_png()))
# except Exception:
#     # This requires some extra dependencies and is optional
#     pass

# %%
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableLambda

from langgraph.prebuilt import ToolNode


def handle_tool_error(state) -> dict:
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            ToolMessage(
                content=f"Error: {repr(error)}\n please fix your mistakes.",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ]
    }


def create_tool_node_with_fallback(tools: list) -> dict:
    return ToolNode(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)], exception_key="error"
    )


def _print_event(event: dict, _printed: set, max_length=1500):
    current_state = event.get("dialog_state")
    if current_state:
        print("Currently in: ", current_state[-1])
    message = event.get("messages")
    if message:
        if isinstance(message, list):
            message = message[-1]
        if message.id not in _printed:
            msg_repr = message.pretty_repr(html=True)
            if len(msg_repr) > max_length:
                msg_repr = msg_repr[:max_length] + " ... (truncated)"
            print(msg_repr)
            _printed.add(message.id)

from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph.message import AnyMessage, add_messages


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    context: Optional[str]


# %%
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage


# Context retrieval function
def retrieve_context(state: State) -> State:
    """Retrieves relevant context from vector store based on the last message."""
    try:
        last_message = None
        for message in reversed(state["messages"]):
            if isinstance(message, HumanMessage):
                last_message = message.content
                break
        
        if last_message:
            context = get_mongo_db.invoke(last_message)
            return {
                "messages": state["messages"],
                "context": context
            }
    except Exception as e:
        print(f"Error retrieving context: {e}")
    
    return {
        "messages": state["messages"],
        "context": None
    }

# # Old
# class Assistant:
#     def __init__(self, runnable: Runnable):
#         self.runnable = runnable

#     def __call__(self, state: State, config: RunnableConfig):
#         while True:
#             configuration = config.get("configurable", {})
#             passenger_id = configuration.get("passenger_id", None)
#             state = {**state, "user_info": passenger_id}
#             result = self.runnable.invoke(state)
#             # If the LLM happens to return an empty response, we will re-prompt it
#             # for an actual response.
#             if not result.tool_calls and (
#                 not result.content
#                 or isinstance(result.content, list)
#                 and not result.content[0].get("text")
#             ):
#                 messages = state["messages"] + [("user", "Respond with a real output.")]
#                 state = {**state, "messages": messages}
#             else:
#                 break
#         return {"messages": result}

# Enhanced Assistant class
class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: State, config: RunnableConfig):
        # Include context in system message if available
        if state.get("context"):
            context_message = f"\nRelevant Context:\n{state['context']}\n"
            temp_messages = state["messages"].copy()
            
            # Update system message with context
            for i, message in enumerate(temp_messages):
                if isinstance(message, SystemMessage):
                    temp_messages[i] = SystemMessage(
                        content=message.content + context_message
                    )
                    break
            
            temp_state = {**state, "messages": temp_messages}
        else:
            temp_state = state

        while True:
            configuration = config.get("configurable", {})
            passenger_id = configuration.get("passenger_id", None)
            temp_state = {**temp_state, "user_info": passenger_id}
            
            result = self.runnable.invoke(temp_state)
            
            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                temp_state = {**temp_state, "messages": messages}
            else:
                break
                
        return {"messages": result, "context": state.get("context")}

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

    IMPORTANT: You must ALWAYS use the 'Book_Appointment' tool to actually book an appointment.
    Convert all time inputs to the format 'HH:MM AM/PM'. Ensure appointments are only scheduled between 09:00 AM and 05:00 PM.
    Never claim an appointment has been booked unless you've used this tool and received a 'BOOKING_CONFIRMED' response.
    If asked to book an appointment, always use the tool and report the exact result to the user.
    ALWAYS maintain a professional and caring tone.
    ALWAYS tabulate suggested doctor in table. The table should contain picture, name and specialty.
    When asked about booked appointment, ask patient to call 0312345678

    If the user has triggered the easter egg 'smart booking', acknowledge it and then ask for a brief health description for each appointment.
    Use this information to determine appropriate appointment durations (30 minutes, 1 hour or 2 hours).
    Before booking, suggest appropriate appointment durations for patient.
"""

# Create prompt template with system message and memory
prompt = ChatPromptTemplate.from_messages([
    ("system", system_message),
    ("placeholder", "{chat_history}"),
    ("human", "{messages}"),
    ("placeholder", "{agent_scratchpad}"),
])


part_1_assistant_runnable = prompt | llm.bind_tools(tools)

# %%
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import tools_condition


# #######
# ##OLD##
# #######
# builder = StateGraph(State)


# # Define nodes: these do the work
# builder.add_node("assistant", Assistant(part_1_assistant_runnable))
# builder.add_node("tools", create_tool_node_with_fallback(tools))
# # Define edges: these determine how the control flow moves
# builder.add_edge(START, "assistant")
# builder.add_conditional_edges(
#     "assistant",
#     tools_condition,
# )
# builder.add_edge("tools", "assistant")


# # The checkpointer lets the graph persist its state
# # this is a complete memory for the entire graph.
# memory = MemorySaver()
# part_1_graph = builder.compile(checkpointer=memory)

# Create the graph with RAG integration
def create_graph():
    builder = StateGraph(State)
    
    # Add nodes
    builder.add_node("retrieve_context", RunnableLambda(retrieve_context))
    builder.add_node("assistant", Assistant(part_1_assistant_runnable))
    builder.add_node("tools", create_tool_node_with_fallback(tools))
    
    # Define the flow
    builder.add_edge(START, "retrieve_context")
    builder.add_edge("retrieve_context", "assistant")
    builder.add_conditional_edges(
        "assistant",
        tools_condition,
    )
    builder.add_edge("tools", "assistant")

    memory = MemorySaver()
    
    return builder.compile(checkpointer=memory)

part_1_graph = create_graph()

config = {
    "configurable": {
        # The passenger_id is used in our flight tools to
        # fetch the user's flight information
        "passenger_id": "3442 587242",
        # Checkpoints are accessed by thread_id
        "thread_id": '1',
    }
}

# questions = [
#     'book me appointment next monday',
#     'any avaialbe doctor at 9am',
#     'currently i am getting headchee, so any doctor should be ok'
# ]

# _printed = set()
# for question in questions:
#     events = part_1_graph.stream(
#         {"messages": ("user", question)}, config, stream_mode="values"
#     )
#     for event in events:
#         _print_event(event, _printed)

# %%
# while True:
#     try:
#         user_input = input("User: ")
#         if user_input.lower() in ["quit", "exit", "q"]:
#             print("Goodbye!")
#             break

#         events = part_1_graph.stream(
#             {"messages": ("user", user_input)}, config, stream_mode="values"
#         )
#         for event in events:
#             _print_event(event, _printed)
#     except:
#         # fallback if input() is not available
#         user_input = "What do you know about LangGraph?"
#         print("User: " + user_input)
#         events = part_1_graph.stream(
#             {"messages": ("user", user_input)}, config, stream_mode="values"
#         )
#         for event in events:
#             _print_event(event, _printed)
#         break


# %%
# @router.post("/gemini_lg")
# async def tooling(chat_request):
#     config = {"configurable": {"thread_id": "2"}}
#     events = graph.stream(
#         {"messages": [("human", chat_request)]}, config, stream_mode="values"
#     )
    
#     results = []
#     for event in events:
#         results.append(event["messages"][-1])        

#     return results[-1].content

# %%

# # Define request model
# class ChatRequest(BaseModel):
#     message: str
#     thread_id: Optional[str] = "1"
#     user_id: Optional[str] = "default_user"

# Define response model
class ChatResponse(BaseModel):
    content: str
    type: str

# Create a Pydantic model for the chat request
class ChatRequest(BaseModel):
    question: str
    session_id: str = Field(default=None, description="Unique identifier for the conversation session")

@router.post("/gemini_graphing")
async def chat_endpoint(chat_request: ChatRequest):
    try:
        # Configure the chat session
        config = {
            "configurable": {
                "thread_id": chat_request.session_id,
            }
        }

        # Process the message through the graph
        events = part_1_graph.stream(
            {"messages": ("user", chat_request.question)}, 
            config, 
            stream_mode="values"
        )

        # Collect all responses
        _printed = set()
        final_ai_response = ""
        
        for event in events:
            if 'messages' in event:
                message = event['messages']
                if isinstance(message, list):
                    message = message[-1]
                if message.id not in _printed:
                    if isinstance(message, AIMessage):
                        final_ai_response = message.content if hasattr(message, 'content') else str(message)
                    _printed.add(message.id)

        # Create the chat history
        # chat_history = [
        #     {
        #         "role": "human",
        #         "content": chat_request.question
        #     },
        #     {
        #         "role": "ai",
        #         "content": final_ai_response
        #     }
        # ]
        chat_history = get_or_create_memory(chat_request.session_id)
        print(chat_history)
        print(final_ai_response)

        # Return the response in the desired format
        return {
            "gemini_response": final_ai_response,
            "chat_history": chat_history
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your request: {str(e)}. "
                  "Please try rephrasing your message or contact support if the issue persists."
        )

from fastapi.responses import StreamingResponse
import json

@router.post("/gemini_stream")
async def stream_chat_endpoint(chat_request: ChatRequest):
    """
    Streaming chat endpoint that processes user messages and returns AI responses as a stream.
    """
    print(chat_request)

    async def response_generator():
        try:
            config = {
                "configurable": {
                    "thread_id": chat_request.session_id,
                }
            }

            events = part_1_graph.stream(
                {"messages": ("user", chat_request.question)}, 
                config, 
                stream_mode="values"
            )

            _printed = set()
            final_ai_response = ""
            
            for event in events:
                if 'messages' in event:
                    message = event['messages']
                    if isinstance(message, list):
                        message = message[-1]
                    if message.id not in _printed:
                        if isinstance(message, AIMessage):
                            final_ai_response = message.content if hasattr(message, 'content') else str(message)
                            response_data = {
                                "gemini_response": final_ai_response,
                                "chat_history": [
                                    {
                                        "role": "human",
                                        "content": chat_request.question
                                    },
                                    {
                                        "role": "ai",
                                        "content": final_ai_response
                                    }
                                ]
                            }
                            yield json.dumps(response_data) + "\n"
                        _printed.add(message.id)

            print(final_ai_response)

        except Exception as e:
            yield json.dumps({"error": str(e)}) + "\n"

    return StreamingResponse(
        response_generator(),
        media_type="application/x-ndjson"
    )
