import sys
sys.path.append('D:/Backend/') 
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from models.database import users_collection


class AvatarEnum(str, Enum):
    avatar1 = 'avatar1'
    avatar2 = 'avatar2'
    avatar3 = 'avatar3'
    avatar4 = 'avatar4'
    avatar5 = 'avatar5'
    avatar6 = 'avatar6'
    avatar7 = 'avatar7'
    avatar8 = 'avatar8'
    avatar9 = 'avatar9'

class User(BaseModel):
    user_id: str  
    username: str
    birth_date: datetime
    gender: str
    occupation: str
    avatar: AvatarEnum  


class UpdateUserData(BaseModel):
    username: Optional[str] = None
    birth_date: Optional[datetime] = None
    avatar: Optional[AvatarEnum] = None
    occupation: Optional[str] = None


async def insert(user_dict):
    user_dict['categories_general'] = ['un_categorized']
    user_dict['categories_scheduled'] = ['un_categorized']
    return  users_collection.insert_one(user_dict)


async def update(user_id: str, user):
    return  users_collection.update_one({"_id": user_id}, {"$set": user})


async def delete(user_id: str):
    return  users_collection.delete_one({"_id": user_id})


async def get(user_id: str):
    return users_collection.find_one({"_id": user_id})
