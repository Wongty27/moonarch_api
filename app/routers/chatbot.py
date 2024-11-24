from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import os
import re
import json
import pandas as pd
import google.generativeai as genai

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

class ProductResponse(BaseModel):
    product_id: int
    product_name: str
    category: str
    sales_price: float
    stock: int

class ChatResponse(BaseModel):
    message: str
    recommended_products: List[ProductResponse]
    total_price: float

load_dotenv()

# Get API key from environment
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

# Set it for the Google API
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

df = pd.read_csv("finalbuilds.csv")   

def initialize_vector_store():
    # Read CSV file 
    # Convert DataFrame to text documents
    documents = []
    for _, row in df.iterrows():
        text = f"""
        Product ID: {row['product_id']}
        Name: {row['product_name']}
        Category: {row['category']}
        Price: {row['sales_price']}
        Stock: {row['stock_count']}
        """
        documents.append(text)
    
    # Create vector store
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key="AIzaSyDSlRGvF5vFugSrRHc_bd0AW1_GPMl6_1A")
    vector_store = FAISS.from_texts(documents, embeddings)
    
    # Store DataFrame for easy lookup
    vector_store.df = df
    
    return vector_store

# Global vector store
VECTOR_STORE = initialize_vector_store()

PROMPT_TEMPLATE = """
You are a PC building expert. Given a budget of RM{budget}, recommend ONE product from EACH category to build a PC.
Target total cost should be as close as possible to RM{budget}, but within RM500 below the budget (acceptable range: RM{budget}-500 to RM{budget}).

Required categories (must include ALL):
- case
- cooler
- cpu
- fan
- gpu
- hdd
- motherboard
- psu
- ram
- ssd

Available products:
{context}

Rules:
1. Total cost must be between RM{budget}-500 and RM{budget}
2. Must select exactly ONE product from EACH category
3. Aim for the closest possible total to RM{budget}
4. Use only the products provided
5. Ensure balanced performance

Respond ONLY with a JSON object in this exact format (no additional text):
{{
    "recommendations": [
        {{
            "product_id": 123,
            "category": "case"
        }},
        {{
            "product_id": 124,
            "category": "cooler"
        }},
        {{
            "product_id": 125,
            "category": "cpu"
        }},
        {{
            "product_id": 126,
            "category": "fan"
        }},
        {{
            "product_id": 127,
            "category": "gpu"
        }},
        {{
            "product_id": 128,
            "category": "hdd"
        }},
        {{
            "product_id": 129,
            "category": "motherboard"
        }},
        {{
            "product_id": 130,
            "category": "psu"
        }},
        {{
            "product_id": 131,
            "category": "ram"
        }},
        {{
            "product_id": 132,
            "category": "ssd"
        }}
    ],
    "reasoning": "Total cost: RM[TOTAL]. Explanation of choices and how they work together."
}}

Remember: The total cost MUST be within RM500 below the budget (RM{budget}-500 to RM{budget}).
"""

@router.post("/chat", response_model=ChatResponse)
async def chat_with_bot(request: ChatRequest):
    try:
        # Extract budget
        budget_match = re.search(r'rm\s*(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s*rm', request.message.lower())
        if not budget_match:
            raise HTTPException(status_code=400, detail="Please specify a budget (e.g., 'Build me a PC not more than RM5000')")
        
        budget = float(budget_match.group(1) or budget_match.group(2))
        
        # Get products context
        context = get_product_context(df)  # We'll define this function
        
        # Generate recommendation
        llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            temperature=0  # Add this to make responses more consistent
        )
        prompt = PromptTemplate(
            input_variables=["budget", "context"],
            template=PROMPT_TEMPLATE
        )
        chain = LLMChain(llm=llm, prompt=prompt)
        
        # Get response and ensure it's JSON
        response = chain.run(budget=budget, context=context)
        
        # Clean and parse response
        try:
            # Remove any non-JSON text
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response[json_start:json_end]
            parsed_response = json.loads(json_str)
            
            # Validate response structure
            if "recommendations" not in parsed_response:
                raise ValueError("Missing 'recommendations' in response")
            if "reasoning" not in parsed_response:
                raise ValueError("Missing 'reasoning' in response")
            
            # Process recommendations
            recommended_products = []
            total_price = 0
            
            for rec in parsed_response["recommendations"]:
                product_id = int(rec["product_id"])
                product_df = df[df['product_id'] == product_id]
                
                if product_df.empty:
                    continue
                    
                product = product_df.iloc[0]
                recommended_products.append(ProductResponse(
                    product_id=product_id,
                    product_name=str(product['product_name']),
                    category=str(product['category']),
                    sales_price=float(product['sales_price']),
                    stock=int(product['stock_count'])
                ))
                total_price += float(product['sales_price'])
            
            return ChatResponse(
                message=parsed_response["reasoning"],
                recommended_products=recommended_products,
                total_price=total_price
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process response: {str(e)}\nResponse was: {response}"
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_product_context(df):
    """Format products for the AI prompt"""
    context_parts = []
    for _, row in df.iterrows():
        context_parts.append(
            f"ID: {row['product_id']}, "
            f"Category: {row['category']}, "
            f"Name: {row['product_name']}, "
            f"Price: RM{row['sales_price']}, "
            f"Stock: {row['stock_count']}"
        )
    return "\n".join(context_parts)
    
# Add an endpoint to refresh products
@router.post("/refresh-products")
async def refresh_products():
    global VECTOR_STORE
    VECTOR_STORE = initialize_vector_store()
    return {"message": "Products refreshed successfully"}

@router.get("/products")
async def get_products():
    return {"products": VECTOR_STORE.df.to_dict(orient="records")}
