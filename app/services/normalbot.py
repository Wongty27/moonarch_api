import os
import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_mongodb.vectorstores import MongoDBAtlasVectorSearch
from langchain_mongodb.cache import MongoDBAtlasSemanticCache
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_core.globals import set_llm_cache

load_dotenv("app/.env")

MONGO_URI = os.getenv("MONGO_URI")
MONGODB_NAME = "moonarch"
COLLECTION_NAME="faq_collection"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GEMINI_API_KEY)
client = MongoClient(MONGO_URI)

# setup semantic cache
semantic_cache = MongoDBAtlasSemanticCache(
    connection_string=MONGO_URI,
    embedding=embedding,
    database_name=MONGODB_NAME,
    collection_name="faq_cache",
    index_name="faq-cache-index",
    score_threshold=0.99
)
set_llm_cache(semantic_cache)

def get_session_history(session_id: str) -> MongoDBChatMessageHistory:
    return MongoDBChatMessageHistory(
        connection_string=MONGO_URI,
        session_id=session_id,
        database_name=MONGODB_NAME,
        collection_name="history"
    )

llm = ChatGoogleGenerativeAI(model='gemini-1.5-flash', api_key=GEMINI_API_KEY)

custom_prompt_template = """You are a knowledgeable and helpful AI customer service. Your primary task is to answer questions based on the information provided to you, but you can also draw on your general knowledge when necessary to provide comprehensive and accurate responses.

Information provided:
{context}

Question: {question}

Instructions:
1. Answer the question directly, concisely, and naturally, as if you're having a conversation.
2. Use the information provided as your primary source, but feel free to expand on it with relevant details or explanations.
3. If you need to make an inference or assumption, do so confidently but reasonably.
4. If the information provided is insufficient, you may draw on your general knowledge to offer a helpful response.
5. Do not provide any external links or webpage.
6. Do not answer questions not related to the information provided.
7. If you truly cannot provide a reliable answer, simply state that you don't have enough information to answer the question accurately.

"""

CUSTOM_PROMPT = PromptTemplate(
    template=custom_prompt_template, input_variables=["context", "question"]
)

df = pd.read_csv('students.csv')


def retrieve_db(question: str):
    agent = create_pandas_dataframe_agent(
        llm,
        df,
        verbose=True,
        allow_dangerous_code=True
    )
    client = MongoClient(os.getenv("MONGO_URI"))
    vector_store = MongoDBAtlasVectorSearch(
        collection=client[MONGODB_NAME][COLLECTION_NAME],
        embedding=GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GEMINI_API_KEY),
        index_name="faq-index",
        relevance_score_fn="cosine",
    )
    try:
        chain = RetrievalQA.from_chain_type(
            retriever=vector_store.as_retriever(),
            llm=llm,
            chain_type_kwargs={"prompt": CUSTOM_PROMPT}
        )

        # user_question = agent
        result = chain.invoke(user_question)
        return result['result'] 
    finally:
        client.close()

