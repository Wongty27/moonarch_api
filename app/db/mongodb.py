# only use for add new data

import os
from dotenv import load_dotenv
from pymongo import MongoClient
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv("app/.env")

MONGODB_NAME = "moonarch"
COLLECTION_NAME="faq_collection"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class MongoDB:
    def __init__(self, db_name: str, collection_name: str, index_name: str):
        self.client = MongoClient(os.getenv("MONGO_URI"))
        embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GEMINI_API_KEY)
        self.vector_store = MongoDBAtlasVectorSearch(
            collection=self.client[db_name][collection_name],
            embedding=embedding,
            index_name=index_name,
            relevance_score_fn="cosine",
        )

    def vector_search_index(self):
        try:
            # Create Vector Search Index
            self.vector_store.create_vector_search_index(dimensions=768, filters=)
            print("Vector Store Created!")
        finally:
            self.client.close()

    def add_documents(self, doc_path: str):
        try:
            # Load and Split PDF
            loader = PyPDFLoader(doc_path)
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            documents = loader.load_and_split(text_splitter=text_splitter)
            self.vector_store.add_documents(documents)
            print("Document Added!")
        finally:
            self.client.close()

# example

# mongo = MongoDB(db_name=MONGODB_NAME, collection_name="history", index_name='faq-index')
# mongo.vector_search_index()
# mongo.add_documents("app/data/FAQ.pdf")