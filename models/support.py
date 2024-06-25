import sys
sys.path.append('D:/Backend/')
from pydantic import BaseModel
from models.database import support_collection
from bson import ObjectId  # Import ObjectId from bson
from typing import List


class Support(BaseModel):
    user_id: str
    email: str
    subject:str
    message: str



def insert_support_messages(support: Support):
    support_dict = support.dict()
    return  support_collection.insert_one(support_dict)

def get_support_messages(user_id: str):
    supports = support_collection.find({"user_id": user_id})
    return [Support(**support) for support in supports]

