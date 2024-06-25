import sys
sys.path.append('D:/Backend/') 
from fastapi import APIRouter, HTTPException
from models.general_tasks import  Step
from controllers.general_tasks_controller import handle_create_general_task
from models.database import general_tasks_collection , users_collection , schedule_tasks_collection



from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson import ObjectId
from pydantic import BaseModel , ValidationError
from enum import Enum
from typing import List, Dict



from fastapi import FastAPI, HTTPException, Query
from pymongo import MongoClient
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import List, Union



class GeneralTask(BaseModel):
    task_name: str
    task_description: str
    steps: List[Step] = None



router = APIRouter()


# add category route 
# this categories will be stored in user document becuase it have no tasks yet "it's new category!"

@router.post("/add-category/{user_id}/{task_type}")
async def add_category(user_id: str, task_type: str, category: str):
    # Check if user exists
    # it will be change after asking mohammed about it
    user = users_collection.find_one({"_id": user_id})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if task type is valid
    if task_type not in ["general", "scheduled"]:
        raise HTTPException(status_code=400, detail="Invalid task type")

    # Create categories field if it doesn't exist yet
    #create 2 lists in user document one for general and one for scheduled
    if f"categories_{task_type}" not in user:
        users_collection.update_one(
            {"_id": user_id},
            {"$set": {f"categories_{task_type}": []}}
        )

    # Check if category already exists in the specified task type
    existing_categories = user.get(f"categories_{task_type}", [])
    if category in existing_categories:
        raise HTTPException(status_code=400, detail="Category already exists")

    # Add the category to the specified task type
    users_collection.update_one(
        {"_id": user_id},
        {"$push": {f"categories_{task_type}": category}}
    )

    # If the task type is general_tasks, check if the category needs to be added to scheduled_tasks as well
    if task_type == "general":
        scheduled_categories = user.get("categories_scheduled", [])
        if category not in scheduled_categories:
            users_collection.update_one(
                {"_id": user_id},
                {"$push": {"categories_scheduled": category}}
            )

    return {"message": "Category added successfully"}





# Pydantic Enums and Models
class TaskStatus(str, Enum):
    completed = "completed"
    in_progress = "in_progress"
    incomplete = "incomplete"

class Step(BaseModel):
    step_name: str
    duration: int  
    status: TaskStatus

class GeneralTask(BaseModel):
    task_name: str
    task_description: str
    category: str
    steps: List[Step]

class ScheduledTask(BaseModel):
    task_name: str
    task_description: str
    steps: List[Step]
    start_time: datetime
    end_time: datetime
    day_date: datetime
    category: str


# Response model
class TaskResponse(BaseModel):

    categories: Dict[str, List[Dict[str, Union[str, List[Step]]]]]





@router.get("/get_tasks_by_category")
async def get_user_tasks(user_id: str, task_type: str) -> TaskResponse:

    # Get user from the database
    user = users_collection.find_one({"_id": user_id})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    categories_key = f"categories_{task_type}"
    categories = user.get(categories_key, [])

    tasks_collection = general_tasks_collection if task_type == "general" else schedule_tasks_collection

    tasks = tasks_collection.find({"user_id": user_id})
#categories_
    categorized_tasks = {}

    for category in categories:
        categorized_tasks[category] = []

    for task in tasks:
        if task_type == "general":
            task_data = GeneralTask(**task)
        else:
            task_data = ScheduledTask(**task)

        if task_data.category in categorized_tasks:
            categorized_tasks[task_data.category].append({
                "task_name": task_data.task_name,
                "task_description": task_data.task_description,
                "steps": [{
                    "step_name": step.step_name,
                    "duration": step.duration,
                    "status": step.status
                } for step in task_data.steps]
            })

    # Include categories with no tasks
    for category in categories:
        if category not in categorized_tasks:
            categorized_tasks[category] = []

    response = TaskResponse(categories=categorized_tasks)
    return response












class GeneralTask2(BaseModel):
    task_name: str
    task_description: str
    steps: List[Step]





class Step(BaseModel):
    step_name: str
    duration: int
    status: str



class ScheduleTask(BaseModel):
    task_name: str
    task_description: str
    steps: List[Step]
    start_time: datetime
    end_time: datetime
    day_date: datetime
    #duration: timedelta = None

class TaskPayload(BaseModel):
    general_task: GeneralTask2 = None
    schedule_task: ScheduleTask = None

@router.post("/add_task", response_model=str)
async def add_task(task_payload: TaskPayload, user_id: str, category: str, task_type: str):
    if task_type == "general" and task_payload.general_task:
        collection = general_tasks_collection
        task = task_payload.general_task
    elif task_type == "schedule" and task_payload.schedule_task:
        collection = schedule_tasks_collection
        task = task_payload.schedule_task
    else:
        raise HTTPException(status_code=400, detail="Invalid task type or missing task payload")

    task_dict = task.dict()

    result = collection.insert_one({
        **task_dict,
        "user_id": user_id,
        "category": category
    })

    if result.inserted_id:
        return "Task inserted successfully!"
    else:
        raise HTTPException(status_code=500, detail="Failed to insert task")