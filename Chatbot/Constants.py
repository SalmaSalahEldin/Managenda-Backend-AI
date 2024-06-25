from pymongo import MongoClient
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
import os

os.environ["OPENAI_API_KEY"] = "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"
os.environ["PINECONE_API_KEY"] = "da2b64b9-04d6-4ac3-b075-a242f4755479"

embeddings = OpenAIEmbeddings()

Mongo_URI = "mongodb+srv://Managenda:Graduationproject2024@cluster0.zs4ebry.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(Mongo_URI)
DB_NAME = "Managenda"
# COLLECTION_NAME = "schedule_tasks"
# MONGODB_COLLECTION = client[DB_NAME][COLLECTION_NAME]

PINECONE_INDEX_NAME = "knowledgebase"
PINECONE_DOSEARCH = PineconeVectorStore(index_name=PINECONE_INDEX_NAME, embedding=embeddings)
