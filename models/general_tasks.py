import sys
sys.path.append('D:/Backend/') 
from typing import List, Dict
from pydantic import BaseModel
from enum import Enum
from models.database import general_tasks_collection

class TaskStatus(str, Enum):
    completed = "completed"
    in_progress = "in_progress"
    incomplete = "incomplete"

class Step(BaseModel):
    step_name: str
    duration: int  
    status: TaskStatus

class GeneralTask(BaseModel):
    user_id: str
    task_name: str
    task_description: str
    category: str
    steps: List[Step]


async def insert_general_task(general_task_dict):
    return  general_tasks_collection.insert_one(general_task_dict)
