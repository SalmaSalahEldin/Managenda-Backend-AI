import pymongo
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_openai import ChatOpenAI
import os
from pymongo import MongoClient
import numpy as np
# from sklearn.metrics.pairwise import cosine_similarity

os.environ["OPENAI_API_KEY"] = "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"

def get_mongo_client():
    return MongoClient(
        "mongodb+srv://Managenda:Graduationproject2024@cluster0.zs4ebry.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
        socketTimeoutMS=600000,  # 60 seconds
        connectTimeoutMS=600000,  # 60 seconds
        serverSelectionTimeoutMS = 600000,  # 60 seconds

    )

def get_similar_tasks(task_names_list, task_name):
    docs = []
    for i in range(len(task_names_list)):
        docs.append(
            Document(
                page_content=task_names_list[i],
                metadata={"task_name": task_names_list[i]}
            )
        )

    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=0)
    texts = text_splitter.split_documents(docs)
    embeddings = OpenAIEmbeddings()
    db = FAISS.from_documents(texts, embeddings)
    vectorstore = Chroma.from_documents(docs, OpenAIEmbeddings())

    metadata_field_info = [
        AttributeInfo(
            name="task_name",
            description="The name of the task that the user has entered",
            type="string",
        )
    ]

    document_content_description = "Name of the tasks that the user has entered before"
    llm = ChatOpenAI(temperature=0)

    retriever = SelfQueryRetriever.from_llm(
        llm,
        vectorstore,
        document_content_description,
        metadata_field_info,
        enable_limit=True,
    )

    res = retriever.invoke(f"I want 1 task with a meaning that most resemebles {task_name}")

    return res[0].metadata['task_name']


def generate_embedding(text: str) -> list[float]:

    embeddings = OpenAIEmbeddings()
    response = embeddings.embed_query(text)

    return response



def get_similar_task(task_name,user_id,search_index,collection_name,path):
    Mongo_URI = "mongodb+srv://Managenda:Graduationproject2024@cluster0.zs4ebry.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    # client = MongoClient(Mongo_URI)
    # client = pymongo.MongoClient(
    #     "mongodb+srv://Managenda:Graduationproject2024@cluster0.zs4ebry.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

    client = get_mongo_client()
    client.admin.command('ping')
    print("MongoDB connection successful.")

    db_name = "Managenda"
    MONGODB_COLLECTION = client[db_name][collection_name]

    results = MONGODB_COLLECTION.aggregate([
      {"$vectorSearch": {
        "queryVector": generate_embedding(task_name),
        "path": path,
        "numCandidates": 100,
        "limit": 1,
        "index": search_index,
          }},
    {"$match":{"user_id": user_id}}

    ])

    res = None
    for result in results:
        res = result["task_name"]

    return res



def cosine_similarity(vec1, vec2):
    if vec1 is None or vec2 is None:
        return -1
    vec1 = np.array(vec1).reshape(1, -1)
    vec2 = np.array(vec2).reshape(1, -1)
    similarity = np.dot(vec1, vec2.T) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    return similarity.item()


def retrieve_most_similar_task_from_the_both_collections(task_name: str, user_id: str):
    schedule_similar_task = get_similar_task(
        task_name.lower(), user_id, "vector_index2", "schedule_tasks", "task_embeddings"
    )
    print('Schedule similar task:', schedule_similar_task)

    general_similar_task = get_similar_task(
        task_name.lower(), user_id, "vector_index", "general_tasks", "task_embeddings"
    )
    print('General similar task:', general_similar_task)

    if not schedule_similar_task and not general_similar_task:
        return None, None

    schedule_embedding = generate_embedding(schedule_similar_task) if schedule_similar_task else None
    general_embedding = generate_embedding(general_similar_task) if general_similar_task else None
    task_embedding = generate_embedding(task_name.lower())

    similarity_schedule = cosine_similarity(task_embedding, schedule_embedding) if schedule_embedding else -1
    similarity_general = cosine_similarity(task_embedding, general_embedding) if general_embedding else -1

    if similarity_general > similarity_schedule:
        print("Similarity of general task is higher")
        return general_similar_task, "general_tasks"

    print("Similarity of schedule task is higher")
    return schedule_similar_task, "schedule_tasks"
