from datetime import datetime, timedelta
import sys
from fastapi import FastAPI, APIRouter, HTTPException ,Query
from collections import defaultdict
from bson import ObjectId
sys.path.append('D:/Backend/') 
from models.database import users_collection ,schedule_tasks_collection
from typing import Optional, Tuple,List, Dict
from datetime import datetime, date, time, timedelta


def calculate_task_status_counts(user_id: str, from_date: datetime.date, to_date: datetime.date = None):
    # Determine start_date and end_date
    start_date = datetime.combine(from_date, datetime.min.time())
    
    if to_date:
        end_date = datetime.combine(to_date, datetime.min.time()) + timedelta(days=1)
    else:
        end_date = start_date + timedelta(days=1)  # Default to daily if to_date is not provided

    # Get task status counts
    task_status_counts = {
        "incomplete": 0,
        "in_progress": 0,
        "completed": 0,
        "pending": 0,
        "total": 0
    }

    # Define the query conditions
    conditions = [
        {"end_time": {"$gte": start_date, "$lt": end_date}, "actual_end_time": {"$exists": False}},  # Tasks with end time within range
        {"start_time": {"$gte": start_date, "$lt": end_date}, "actual_start_time": {"$exists": False}},  # Tasks with start time within range
        {"actual_end_time": {"$gte": start_date, "$lt": end_date}},  # Completed tasks within range
        {"actual_start_time": {"$gte": start_date, "$lt": end_date}, "actual_end_time": {"$exists": False}}, # Completed tasks within range
        {  # Tasks that are (pending or in progress) and times before the range "delayed tasks"
            "$or": [
                {"start_time": {"$lt": start_date}},
                {"end_time": {"$lt": start_date}}
            ],
            "$and": [
                {"$or": [
                    {"start_time": {"$exists": True}, "actual_start_time": {"$exists": False}},
                    {"end_time": {"$exists": True}, "actual_end_time": {"$exists": False}},
                    {
                        "start_time": {"$exists": True},
                        "end_time": {"$exists": True},
                        "$or": [
                            {"actual_start_time": {"$exists": True}, "actual_end_time": {"$exists": False}},
                            {"actual_start_time": {"$exists": False}, "actual_end_time": {"$exists": False}}
                        ]
                    }
                ]}
            ]
        },
        {  # Include tasks without start_time and end_time "pending only so there is no actual_end"
           # if thay are completed so thay have actual end thay will be returned if thay within range only "condition 3"
            "start_time": {"$exists": False},
            "end_time": {"$exists": False},
            "actual_end_time": {"$exists": False}
        }
    ]

    # Get tasks for the user within the specified timeframe
    tasks = schedule_tasks_collection.find({
        "user_id": user_id,
        "$or": conditions
    })

    # Count tasks for each status and print task names
    for task in tasks:
        task_status = task.get("task_status")
        
        # Print the task name or identifier
        task_name = task.get("task_name")  # Change "name" to the appropriate field
        print(f"Task Name: {task_name}, Status: {task_status}")
        
        if task_status in task_status_counts:
            task_status_counts[task_status] += 1

    # Sum up all the counts to get the total
    task_status_counts["total"] = sum(task_status_counts.values())

    # Calculate productivity score
    total_tasks = task_status_counts["total"]
    completed_tasks = task_status_counts["completed"]
    productivity_score = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0

    return task_status_counts, productivity_score


# Function to calculate completed tasks per week
def calculate_completed_tasks_per_date_range(user_id: str, from_date: datetime.date, to_date: datetime.date = None):
    # Define start_date and end_date
    start_date = datetime.combine(from_date, datetime.min.time())

    if to_date:
        end_date = datetime.combine(to_date, datetime.min.time()) + timedelta(days=1)
    else:
        end_date = start_date + timedelta(days=7)  # Default to a weekly timeframe if to_date is not provided

    
    # Initialize a defaultdict to store completed tasks per day
    completed_tasks_per_day = defaultdict(int)

    # Get tasks for the user within the specified date range
    tasks = schedule_tasks_collection.find({
        "user_id": user_id,
        "task_status": "completed",
        "actual_end_time": {"$exists": True, "$gte": start_date, "$lt": end_date}
    })

    # Aggregate completed tasks per day
    for task in tasks:
        if task.get("task_status") == "completed":
            task_date = task["actual_end_time"].date()
            task_date_str = task_date.strftime("%Y-%m-%d")  # Format date without day name
            day_name = task_date.strftime("%A")  # Get day name
            completed_tasks_per_day[f"{task_date_str} - {day_name}"] += 1  # Combine date and day name

    # Fill in days with zero completed tasks
    current_date = start_date
    while current_date < end_date:
        current_date_str = current_date.strftime("%Y-%m-%d")  # Format date without day name
        day_name = current_date.strftime("%A")  # Get day name
        combined_date = f"{current_date_str} - {day_name}"  # Combine date and day name
        if combined_date not in completed_tasks_per_day:
            completed_tasks_per_day[combined_date] = 0
        current_date += timedelta(days=1)

    # Find the day with the maximum completed tasks count
    max_completed_day = max(completed_tasks_per_day, key=completed_tasks_per_day.get)

    return completed_tasks_per_day, max_completed_day



def get_tasks_with_actual_times(user_id: str, from_date: datetime.date, to_date: Optional[datetime.date] = None) -> List[Dict]:
    # Define start_date and end_date
    start_date = datetime.combine(from_date, datetime.min.time())

    if to_date:
        end_date = datetime.combine(to_date, datetime.min.time()) + timedelta(days=1)
    else:
        end_date = start_date + timedelta(days=1)  # Default to a daily timeframe if to_date is not provided

    # Get tasks for the user within the specified date range
    tasks = schedule_tasks_collection.find({
        "user_id": user_id,
        "start_time": {"$exists": True},
        "end_time": {"$exists": True},
        "actual_start_time": {"$exists": True},
        "actual_end_time": {"$exists": True},
        "end_time": {"$gte": start_date, "$lt": end_date}
    })

    # Initialize a list to store tasks with actual times
    tasks_with_actual_times = []

    # Iterate over tasks and filter those with actual times
    for task in tasks:
        # Calculate estimated duration
        estimated_duration = task["end_time"] - task["start_time"]

        # Calculate actual duration
        actual_duration = task["actual_end_time"] - task["actual_start_time"]

        task_data = {
            "task_id": str(task["_id"]),  # Convert ObjectId to string
            "task_name": task.get("task_name"),
            "start_time": task["start_time"],
            "end_time": task["end_time"],
            "actual_start_time": task["actual_start_time"],
            "actual_end_time": task["actual_end_time"],
            "estimated_duration": estimated_duration.total_seconds() / 3600,  # Convert to hours
            "actual_duration": actual_duration.total_seconds() / 3600  # Convert to hours
        }
        tasks_with_actual_times.append(task_data)

    return tasks_with_actual_times

def calculate_task_completion_percentage(user_id: str, from_date: date, to_date: Optional[date] = None) -> Optional[Tuple[float, float]]:
    # Define start_date and end_date
    start_date = datetime.combine(from_date, datetime.min.time())

    if to_date:
        end_date = datetime.combine(to_date, datetime.min.time()) + timedelta(days=1)
    else:
        end_date = start_date + timedelta(days=1)  # Default to a daily timeframe if to_date is not provided

    # Define morning and evening time ranges
    morning_start_time = time(6, 0)
    morning_end_time = time(15, 0)
    evening_start_time = time(15, 1)
    evening_end_time = time(23, 59)

    # Get tasks for the user within the specified date range
    tasks = schedule_tasks_collection.find({
        "user_id": user_id,
        "task_status": "completed",
        "actual_end_time": {"$gte": start_date, "$lt": end_date}
    })

    # Initialize counts for tasks completed in morning and evening hours
    morning_tasks_completed = 0
    evening_tasks_completed = 0
    total_tasks = 0

    # Count tasks completed in morning and evening hours
    for task in tasks:
        total_tasks += 1
        actual_start_time = task.get("actual_start_time")
        actual_end_time = task.get("actual_end_time").time() if task.get("actual_end_time") else None

        # Check if the task falls within morning hours
        if actual_start_time:
            actual_start_time = actual_start_time.time()
            if morning_start_time <= actual_start_time <= morning_end_time or (actual_end_time and morning_start_time <= actual_end_time <= morning_end_time):
                morning_tasks_completed += 1
        
        # Check if the task falls within evening hours
        if actual_start_time:
            if evening_start_time <= actual_start_time <= evening_end_time or (actual_end_time and evening_start_time <= actual_end_time <= evening_end_time):
                evening_tasks_completed += 1

    # Calculate the percentage of tasks completed in morning and evening hours
    total_morning_percentage = (morning_tasks_completed / total_tasks) * 100 if total_tasks > 0 else 0
    total_evening_percentage = (evening_tasks_completed / total_tasks) * 100 if total_tasks > 0 else 0

    return total_morning_percentage, total_evening_percentage

from datetime import datetime

from datetime import datetime, time

from datetime import datetime

def get_tasks_completion_ratio(user_id: str, from_date: datetime, to_date: Optional[datetime] = None):
    # Convert from_date to datetime object with the minimum time
    start_date = datetime.combine(from_date, datetime.min.time())

    # If to_date is not provided, set it to the last second of that day (from_date)
    if not to_date:
        to_date = datetime.combine(from_date, datetime.max.time())
    
    # Convert to_date to datetime object with the maximum time
    end_date = datetime.combine(to_date, datetime.max.time())

    print(start_date)
    print(end_date)
    
    # Define the query based on tasks within the specified date range
    query = {
        "user_id": user_id,
        "$or": [
            {
                "actual_end_time": {"$exists": True},
                "end_time": {"$gte": start_date, "$lte": end_date}
            },
            {
                "end_time": {"$exists": False},
                "actual_start_time": {"$exists": True},
                "start_time": {"$gte": start_date, "$lte": end_date}
            }
        ]
    }

    tasks = list(schedule_tasks_collection.find(query))
    
    total_completed_tasks = 0
    on_time_tasks = 0
    early_tasks = 0
    delay_tasks = 0

    # Define a grace period of 5 minutes
    grace_period = timedelta(minutes=5)

    for task in tasks:
        total_completed_tasks += 1

        # Check if the task is on time, early, or delayed based on available fields
        if "actual_end_time" in task:
            actual_end_time = task["actual_end_time"]
            scheduled_end_time = task["end_time"]
            if abs(actual_end_time - scheduled_end_time) <= grace_period:
                on_time_tasks += 1
            elif actual_end_time < scheduled_end_time:
                early_tasks += 1
            else:
                delay_tasks += 1
        elif "actual_start_time" in task:
            actual_start_time = task["actual_start_time"]
            scheduled_start_time = task["start_time"]
            if abs(actual_start_time - scheduled_start_time) <= grace_period:
                on_time_tasks += 1
            elif actual_start_time < scheduled_start_time:
                early_tasks += 1
            else:
                delay_tasks += 1

    return {
        "total_tasks": total_completed_tasks,
        "on_time_tasks": on_time_tasks,
        "early_tasks": early_tasks,
        "delay_tasks": delay_tasks
    }

router = APIRouter()

    # Function to validate user ID
def validate_user_info(user_id: str, date: str):
    user = users_collection.find_one({"_id": user_id})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    # Parse the input date
    try:
        input_date = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Please use yyyy-mm-dd.")
    return input_date


@router.get("/calculate_metrics/{user_id}")
async def calculate_metrics_endpoint(user_id: str, from_date: str, to_date: Optional[str] = None):
    try:
        # Validate and parse input dates
        input_from_date = validate_user_info(user_id, from_date)
        input_to_date = validate_user_info(user_id, to_date) if to_date else None

        # Calculate task status counts
        task_status_counts, productivity_score = calculate_task_status_counts(user_id, input_from_date, input_to_date)
        # Calculate completed tasks and the day with the most completed tasks
        completed_tasks_per_day, max_completed_day = calculate_completed_tasks_per_date_range(user_id, input_from_date, input_to_date)

        # Get tasks with actual times
        tasks_actual_times = get_tasks_with_actual_times(user_id, input_from_date, input_to_date)

        # Calculate task completion ratio
        task_completion_ratio = get_tasks_completion_ratio(user_id,input_from_date,
         input_to_date if 'input_to_date' in locals() and input_to_date else None)

        # Calculate task completion percentage
        morning_evening_percentage = calculate_task_completion_percentage(user_id, input_from_date, input_to_date)

        # Check if morning_evening_percentage is not None before accessing its elements
        if morning_evening_percentage is not None:
            morning_percentage, evening_percentage = morning_evening_percentage
        else:
            morning_percentage, evening_percentage = None, None

        # Return the results
        return {
            "task_status_counts": task_status_counts,
            "productivity_score": productivity_score,
            "completed_tasks": completed_tasks_per_day,
            "max_completed_day": max_completed_day,
            "tasks_actual_times":tasks_actual_times,
                "morning_evening_percentage": {
                "morning": morning_percentage,
                "evening": evening_percentage
        },
            "task_completion_ratio": task_completion_ratio
        }


    except HTTPException as e:
        raise e  # Re-raise HTTPException for consistent error handling

