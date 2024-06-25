import sys
sys.path.append('D:/Backend/') 
from pydantic import BaseModel
from typing import List 
from datetime import datetime, timedelta
from enum import Enum
from models.database import schedule_tasks_collection

class TaskStatus(str, Enum):
    completed = "completed"
    in_progress = "in_progress"
    incomplete = "incomplete"

class Step(BaseModel):
    step_name: str
    duration: int  
    status: TaskStatus

class ScheduleTask(BaseModel):
    task_id: str
    user_id: str
    task_name: str
    task_description: str
    steps: List[Step]
    start_time: datetime
    actual_start_time: datetime = None
    end_time: datetime
    actual_end_time: datetime = None
    day_date: datetime
    status: TaskStatus
    task_category: str
    duration: timedelta = None
    actual_duration: timedelta = None

async def insert_schedule_task(schedule_task_dict):
    return schedule_tasks_collection.insert_one(schedule_task_dict)
