# Pinecone (performance/ storage)
import os
from typing import List
from langchain.schema import Document
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_community.document_loaders import UnstructuredFileLoader
from openai import OpenAI
from Chatbot import Constants

# Set environment variables securely
os.environ["OPENAI_API_KEY"] = ""
os.environ["PINECONE_API_KEY"] = ""

index_name = Constants.PINECONE_INDEX_NAME
docsearch = Constants.PINECONE_DOSEARCH

# Initialize clients and embeddings
openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
embeddings = OpenAIEmbeddings()

def load_documents(folder_path: str) -> List[Document]:
    documents = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.pdf'):
            file_path = os.path.join(folder_path, file_name)
            loader = UnstructuredFileLoader(file_path)
            documents.extend(loader.load())
    return documents

def chunk_documents(documents: List[Document]) -> List[Document]:
    text_splitter = SemanticChunker(embeddings)
    chunked_docs = []
    for doc in documents:
        chunks = text_splitter.create_documents([doc.page_content])
        chunked_docs.extend(chunks)
    return chunked_docs

def create_metadata(doc: Document, filename: str) -> dict:
    meta_data = doc.metadata if doc.metadata else {}
    meta_data["Title"] = filename if "Title" not in meta_data else filename + ".pdf"
    return meta_data


def store_documents(documents: List[Document], index_name: str) -> None:
    try:
        # Initialize the existing vector store
        vectorstore = PineconeVectorStore(index_name=index_name, embedding=embeddings)

        # Add documents to the vector store
        for i, doc in enumerate(documents):
            doc_id = f"{doc.metadata.get('Title', 'doc')}_id{i}"
            vectorstore.add_texts(texts=[doc.page_content], metadatas=[doc.metadata], ids=[doc_id],
                                  index_name=index_name)

    except RuntimeError as e:
        print(f"RuntimeError encountered: {e}")
        # If there's an error (e.g., vector store does not exist), create it from documents
        vectorstore = PineconeVectorStore.from_documents(documents, embeddings, index_name=index_name)

    print(f"Documents successfully stored in the vector store with index: {index_name}")


def create_db(folder_path: str) -> str:
    documents = load_documents(folder_path)
    chunked_documents = chunk_documents(documents)
    for doc in chunked_documents:
        filename = os.path.basename(doc.metadata["source"]) if "source" in doc.metadata else "unknown"
        doc.metadata = create_metadata(doc, filename)
    store_documents(chunked_documents, index_name=index_name)
    return "done inserting files"

# Example usage
folder_path = "/home/salma/GraduationProject/PDFs"
print(create_db(folder_path))




# Mondodb Atlas (general purpose/ limited storage)

# import os
# from typing import List
# from pymongo import MongoClient
# from langchain.schema import Document
# from langchain_experimental.text_splitter import SemanticChunker
# from langchain_openai import OpenAIEmbeddings
# from langchain_community.document_loaders import UnstructuredFileLoader
# from openai import OpenAI
#
# # Set environment variables securely
# os.environ["OPENAI_API_KEY"] = "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"
# Mongo_URI = "mongodb+srv://Managenda:Graduationproject2024@cluster0.zs4ebry.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# DB_NAME = "Managenda"
# COLLECTION_NAME = "knowledgebase"
#
# # Initialize MongoDB client
# client = MongoClient(Mongo_URI)
# db = client[DB_NAME]
# collection = db[COLLECTION_NAME]
#
# # Initialize OpenAI client and embeddings
# openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
# embeddings = OpenAIEmbeddings()
#
# def load_documents(folder_path: str) -> List[Document]:
#     documents = []
#     for file_name in os.listdir(folder_path):
#         if file_name.endswith('.pdf'):
#             file_path = os.path.join(folder_path, file_name)
#             loader = UnstructuredFileLoader(file_path)
#             docs = loader.load()
#             for doc in docs:
#                 doc.metadata = doc.metadata or {}
#                 doc.metadata["Title"] = file_name[:-4]  # Set the title without .pdf extension
#             documents.extend(docs)
#     return documents
#
# def chunk_documents(documents: List[Document]) -> List[Document]:
#     text_splitter = SemanticChunker(embeddings)
#     chunked_docs = []
#     for doc in documents:
#         chunks = text_splitter.create_documents([doc.page_content])
#         for chunk in chunks:
#             chunk.metadata = doc.metadata
#         chunked_docs.extend(chunks)
#     return chunked_docs
#
# def store_documents(documents: List[Document]) -> None:
#     for i, doc in enumerate(documents):
#         title = doc.metadata.get('Title', 'doc')
#         doc_id = f"{title}_id{i}"
#         doc.metadata["ID"] = doc_id
#         vector = embeddings.embed_query(doc.page_content)
#         document_data = {
#             "text": doc.page_content,
#             "metadata": doc.metadata,
#             "embeddings": vector
#         }
#         collection.insert_one(document_data)
#
#     print("Documents successfully stored in MongoDB collection.")
#
# def create_db(folder_path: str) -> str:
#     documents = load_documents(folder_path)
#     chunked_documents = chunk_documents(documents)
#     store_documents(chunked_documents)
#     return "done inserting files"
#
# # Example usage
# folder_path = "/home/salma/GraduationProject/PDFs"
# print(create_db(folder_path))
