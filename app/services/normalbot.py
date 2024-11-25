import os
from dotenv import load_dotenv
from pymongo import MongoClient
from app.schemas import AiResponse
from langchain_mongodb.vectorstores import MongoDBAtlasVectorSearch
from langchain_mongodb.cache import MongoDBAtlasSemanticCache
from langchain_core.output_parsers import PydanticOutputParser, JsonOutputParser
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_core.globals import set_llm_cache

load_dotenv("app/.env")
MONGO_URI = os.getenv("MONGO_URI")
MONGODB_NAME = "moonarch"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GEMINI_API_KEY)
semantic_cache = MongoDBAtlasSemanticCache(
    connection_string=MONGO_URI,
    embedding=embedding,
    database_name=MONGODB_NAME,
    collection_name="faq_cache",
    index_name="faq-cache-index",
    score_threshold=0.99
)
set_llm_cache(semantic_cache)

llm = ChatGoogleGenerativeAI(
    model='gemini-1.5-flash',
    api_key=GEMINI_API_KEY
)

custom_prompt_template = """You are a knowledgeable and helpful AI customer service. Your primary task is to answer questions based on the customer's intention provided to you, but you can also draw on your general knowledge when necessary to provide comprehensive and accurate responses.

Information provided:
{context}

Question: {question} \n {format_instructions}

Instructions:
1. Answer the question directly, concisely, and naturally, as if you're having a conversation.
2. Use the information provided as your primary source, but feel free to expand on it with relevant details or explanations.
3. If you need to make an inference or assumption, do so confidently but reasonably.
4. If the information provided is insufficient, you may draw on your general knowledge to offer a helpful response.
5. Do not provide any external links or webpage.
6. Do not answer questions not related to the information provided.
7. If you truly cannot provide a reliable answer, simply state that you don't have enough information to answer the question accurately.
"""
parser = PydanticOutputParser(pydantic_object=AiResponse)

CUSTOM_PROMPT = PromptTemplate(
    template=custom_prompt_template,
    input_variables=["context", "question"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

def call_model(question):
    client = MongoClient(MONGO_URI)
    vector_store = MongoDBAtlasVectorSearch(
        collection=client[MONGODB_NAME]["chatbot_collection"],
        embedding=embedding,
        index_name='chatbot-index',
        relevance_score_fn="cosine",
    )
    try:
        chain = RetrievalQA.from_chain_type(
            retriever=vector_store.as_retriever(),
            llm=llm,
            chain_type_kwargs={"prompt": CUSTOM_PROMPT}
        )        
        response = chain.invoke(question)     
        return response["result"]
    finally:
        client.close()
