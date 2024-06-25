from datetime import datetime
import sys

from pydantic import BaseModel
sys.path.append('D:/Backend/') 
from fastapi import APIRouter
from models.schedule_tasks import ScheduleTask
from controllers.schedule_tasks_controller import create_schedule_task
from models.database import schedule_tasks_collection

router = APIRouter()

@router.post("/schedule_tasks/")
async def route_create_schedule_task(task: ScheduleTask):
    return await create_schedule_task(task)




@router.post("/tasks/")

async def create_task(user_id :str, task_name: str, start_time: datetime, end_time: datetime, insert_anyway: bool = False):
    # Check for overlapping tasks
    tasks_collection = schedule_tasks_collection
    overlapping_tasks = tasks_collection.find({'user_id': user_id,
        '$or': [
            {'start_time': {'$lt': end_time}, 'end_time': {'$gt': start_time}},
            {'start_time': {'$gte': start_time, '$lte': end_time}},
            {'end_time': {'$gte': start_time, '$lte': end_time}}
        ]
    })
    
    overlapping_task_list = list(overlapping_tasks)
    
    if overlapping_task_list:
        # Handle overlapping tasks
        if insert_anyway:
            # Insert the task anyway
            new_task = {
                "task_name": task_name,
                "start_time": start_time,
                "end_time": end_time
            }
            task_id = tasks_collection.insert_one(new_task).inserted_id
            return {"message": "Task inserted despite conflicts", "task_id": str(task_id)}
        else:
            # Return conflicting tasks and options to the user
            return {
                "message": "Task conflicts with existing tasks",
                "conflicting_tasks": overlapping_task_list,
                "options": ["Insert anyway", "Edit task timing"]
            }
    else:
        # Insert the task if there are no conflicts
        new_task = {
            "task_name": task_name,
            "start_time": start_time,
            "end_time": end_time
        }
        task_id = tasks_collection.insert_one(new_task).inserted_id
        return {"message": "Task created successfully", "task_id": str(task_id)}
    




































