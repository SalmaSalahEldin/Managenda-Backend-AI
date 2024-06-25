import sys
from fastapi import HTTPException
sys.path.append('D:/Backend/') 
from typing import List, Optional , Dict ,Union
from pydantic import BaseModel, Field, validator, root_validator,ValidationError
from datetime import datetime , timedelta
from enum import Enum
from models.database import users_collection , general_tasks_collection , schedule_tasks_collection
from bson import ObjectId
from datetime import datetime


# Pydantic Enums and Models

class TaskStatus(str, Enum):
    in_progress = "in_progress"
    completed = "completed"
    incomplete = "incomplete"
    pending="pending"

class Step(BaseModel):
    step_name: str
    step_status: Optional[TaskStatus] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    start_notif_id: Optional[int] = None
    end_notif_id: Optional[int] = None

class Step_add(BaseModel):
    step_name: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    start_notif_id: Optional[int] = None
    end_notif_id: Optional[int] = None

class Step_general(BaseModel):
    step_name: str
    duration: Optional[int]   

class ScheduledTask_get(BaseModel):
    task_name: Optional[str] 
    steps: Optional[List[Step]] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    category: Optional[str] = None
    task_status: Optional[TaskStatus] = None
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    start_notif_id: Optional[int] = None
    end_notif_id: Optional[int] = None

class GeneralTask_get(BaseModel):
    task_name: Optional[str] = None
    category: Optional[str] = None
    steps: Optional[List[Step_general]] = None

# users don't have to insert catecory when that put any task
# class GeneralTask_add(BaseModel):
#     task_name: str
#     steps: Optional[List[Step_general]] = []

# users don't have to insert catecory when that put any task
# class ScheduledTask_add(BaseModel):
#     task_name: str
#     steps: Optional[List[Step_add]] = None
#     start_time: Optional[datetime] = None
#     end_time: Optional[datetime] =None
#     start_notif_id: Optional[int] = None
#     end_notif_id: Optional[int] = None


class GeneralTask_add(BaseModel):
    task_name: str
    embeddings: Optional[List[float]] = None
    steps: Optional[List[Step_general]] = []


class ScheduledTask_add(BaseModel):
    task_name: str
    embeddings: Optional[List[float]] = None
    steps: Optional[List[Step_add]] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    start_notif_id: Optional[int] = None
    end_notif_id: Optional[int] = None



class GeneralTaskResponse(BaseModel):
    categories: Dict[str, List[Dict[str, Union[str, List[Step_general]]]]]


class ScheduledTaskResponse(BaseModel):
    categories: Dict[str, List[Dict[str, Union[str, List[Step]]]]]

class TaskResponse(BaseModel):
    categories: Dict[str, List[Dict[str, Union[str, List[Union[Step, Step_general]]]]]]



class TaskPayload(BaseModel):
    general_task: GeneralTask_add = None
    schedule_task: ScheduledTask_add = None

class TaskPayload2(BaseModel):
    scheduled_task: Optional[ScheduledTask_get] = None
    general_task: Optional[GeneralTask_get] = None


def add_category(user_id: str, task_type: str, category: str):
    user = users_collection.find_one({"_id": user_id})
    if user is None:
        raise ValueError("User not found")

    if task_type not in ["general", "scheduled"]:
        raise ValueError("Invalid task type")
    #we will use this first time user insert category to initialize 2 arrays
    if f"categories_{task_type}" not in user:
        users_collection.update_one(
            {"_id": user_id},
            {"$set": {f"categories_{task_type}": []}}
        )

    existing_categories = user.get(f"categories_{task_type}", [])
    if category in existing_categories:
        return False  # Category already exists

    users_collection.update_one(
        {"_id": user_id},
        {"$push": {f"categories_{task_type}": category}}
    )
    return True  # Category was newly added



def get_general_tasks_with_category(user_id: str ) -> GeneralTaskResponse:
    user = users_collection.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    categories = user.get("categories_general", [])
    tasks_collection = general_tasks_collection
    tasks = tasks_collection.find({"user_id": user_id})

    categorized_tasks = {}

    for category in categories:
        categorized_tasks[category] = []

    for task in tasks:
        # Convert ObjectId to string for task ID
        task_id = str(task.pop("_id"))

        task_data = GeneralTask_get(**task)
        task_details = {"task_id": task_id, "task_name": task_data.task_name}

        if hasattr(task_data, "task_status") and task_data.task_status is not None:
            task_details["task_status"] = task_data.task_status.value

        if hasattr(task_data, "steps") and task_data.steps is not None:
            task_details["steps"] = []
            for step in task_data.steps:
                if isinstance(step, Step_general):
                    step_info = {"step_name": step.step_name}
                    if step.duration is not None:
                        step_info["duration"] = step.duration
                    task_details["steps"].append(step_info)

        if hasattr(task_data, "start_time") and task_data.start_time is not None:
            task_details["start_time"] = str(task_data.start_time)

        if hasattr(task_data, "end_time") and task_data.end_time is not None:
            task_details["end_time"] = str(task_data.end_time)

        categorized_tasks[task_data.category].append(task_details)

    for category in categories:
        if category not in categorized_tasks:
            categorized_tasks[category] = []

    response = GeneralTaskResponse(categories=categorized_tasks)
    return response



def get_scheduled_tasks_with_category(user_id: str ) -> ScheduledTaskResponse:
    user = users_collection.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    categories = user.get("categories_scheduled", [])
    tasks_collection = schedule_tasks_collection
    tasks = tasks_collection.find({"user_id": user_id})

    categorized_tasks = {}

    for category in categories:
        categorized_tasks[category] = []

    for task in tasks:
        # Convert ObjectId to string for task ID
        task_id = str(task.pop("_id"))

        task_data = ScheduledTask_get(**task)
        task_details = {"task_id": task_id, "task_name": task_data.task_name}


        if hasattr(task_data, "task_status") and task_data.task_status is not None:
            task_details["task_status"] = task_data.task_status.value

        if hasattr(task_data, "steps") and task_data.steps is not None:
            task_details["steps"] = [step.dict() for step in task_data.steps]

        if hasattr(task_data, "start_time") and task_data.start_time is not None:
            task_details["start_time"] = str(task_data.start_time)

        if hasattr(task_data, "end_time") and task_data.end_time is not None:
            task_details["end_time"] = str(task_data.end_time)

        if hasattr(task_data, "actual_start_time") and task_data.actual_start_time is not None:
            task_details["actual_start_time"] = str(task_data.actual_start_time)

        if hasattr(task_data, "actual_end_time") and task_data.actual_end_time is not None:
            task_details["actual_end_time"] = str(task_data.actual_end_time)

        if hasattr(task_data, "status") and task_data.status is not None:
            task_details["status"] = task_data.status

        if hasattr(task_data, "start_notif_id") and task_data.start_notif_id is not None:
            task_details["start_notif_id"] = str(task_data.start_notif_id)

        if hasattr(task_data, "end_notif_id") and task_data.end_notif_id is not None:
            task_details["end_notif_id"] = str(task_data.end_notif_id)

        categorized_tasks[task_data.category].append(task_details)

    for category in categories:
        if category not in categorized_tasks:
            categorized_tasks[category] = []

    response = ScheduledTaskResponse(categories=categorized_tasks)
    return response


def parse_datetime(dt_str):
    try:
        return datetime.fromisoformat(dt_str)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid datetime format: {dt_str}")


from Chatbot.SelfQuery import generate_embedding

def add_task_to_category(task_payload: TaskPayload, user_id: str, category: str, task_type: str, insert_anyway: bool = False):

     # Check if category and user exist or not
     # incase we try to initiate the templet and the category is not exist we create the category on the fly
    user = users_collection.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    categories_key = f"categories_{task_type}"
    categories = user.get(categories_key, [])
    if category not in categories:
        if task_type == "scheduled":
            try:
                # Attempt to add the category if it doesn't exist
                add_category(user_id, task_type, category)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=f"Category '{category}' does not exist")
    
    if task_type == "general" and task_payload.general_task:
        collection = general_tasks_collection
        task = task_payload.general_task
        existing_task = collection.find_one({"user_id": user_id, "task_name": task.task_name, "category": category})
        if existing_task:
            raise HTTPException(status_code=400, detail="Task name must be unique within the same category!")
    
        task_dict = task.dict(exclude_unset=True)  # Exclude fields not explicitly set
        # Generate embeddings for the task name
        task_dict['embeddings'] = generate_embedding(task.task_name)

        # Include steps only if provided
        steps = task_dict.pop("steps", None)

        # Insert without task status or step status for general tasks
        insertion_dict = {
            **task_dict,
            "user_id": user_id,
            "category": category,
        }

        # Include steps in insertion dict only if provided
        if steps is not None:
            for step in steps:
                if 'start_time' in step and isinstance(step['start_time'], str):
                    step['start_time'] = parse_datetime(step['start_time'])
                if 'end_time' in step and isinstance(step['end_time'], str):
                    step['end_time'] = parse_datetime(step['end_time'])
            insertion_dict["steps"] = steps

        result = collection.insert_one(insertion_dict)

    elif task_type == "scheduled" and task_payload.schedule_task:
        collection = schedule_tasks_collection
        task = task_payload.schedule_task

        task_dict = task.dict(exclude_unset=True)  # Exclude fields not explicitly set
        # Generate embeddings for the task name
        task_dict['embeddings'] = generate_embedding(task.task_name)
        # Include steps only if provided
        steps = task_dict.pop("steps", None)

        # Insert without task status or step status for scheduled tasks
        insertion_dict = {
            **task_dict,
            "user_id": user_id,
            "category": category,
            "task_status": "pending"

        }

        # Include steps in insertion dict only if provided
        if steps is not None:
            for step in steps:
                if 'start_time' in step and isinstance(step['start_time'], str):
                    step['start_time'] = parse_datetime(step['start_time'])
                if 'end_time' in step and isinstance(step['end_time'], str):
                    step['end_time'] = parse_datetime(step['end_time'])                
            insertion_dict["steps"] = steps

            # Add "task_status": "pending" to each step
            for step in insertion_dict["steps"]:
                step["step_status"] = "pending"

        # Include start_time and end_time in insertion dict only if provided
        if "start_time" in task_dict and isinstance(task_dict["start_time"], str):
            insertion_dict["start_time"] = parse_datetime(task_dict["start_time"])
        if "end_time" in task_dict and isinstance(task_dict["end_time"], str):
            insertion_dict["end_time"] = parse_datetime(task_dict["end_time"])

        # Check for overlapping tasks only if both start_time and end_time are provided
        if "start_time" in insertion_dict and "end_time" in insertion_dict:
            overlapping_tasks = collection.find({
                            'user_id': user_id,
                            '$or': [
                                {'start_time': {'$lt': insertion_dict['end_time']}, 'end_time': {'$gt': insertion_dict['start_time']}},
                                {'start_time': insertion_dict['start_time'], 'end_time': insertion_dict['end_time']}
                            ]
                        })
            overlapping_task_list = list(overlapping_tasks)
            if overlapping_task_list:
                if insert_anyway:
                    default_status = "pending"
                    result = collection.insert_one({
                        **insertion_dict,
                        "task_status": default_status
                    })
                    return {"message": "Task inserted despite conflicts", "task_id": str(result.inserted_id)}
                else:
                    return {
                        "message": "Task conflicts with existing tasks",
                        "conflicting_tasks": overlapping_task_list,
                        "options": ["Insert anyway", "Edit task timing"]
                    }

        # If there are no conflicts or overlapping tasks, insert the task
        result = collection.insert_one(insertion_dict)

    else:
        raise HTTPException(status_code=400, detail="Invalid task type or missing task payload")


    return result.inserted_id



def delete_category(user_id: str, task_type: str, category_name: str) -> bool:
    # Check if the category is "un_categorized" and if so, return without deletion

    if category_name == "un_categorized":
        print("This category cannot be deleted.")
        return False

    # Check if the task_type is valid
    if task_type not in ["general", "scheduled"]:
        raise HTTPException(status_code=400, detail="Invalid task type")

    
    # Find the user by user_id
    user = users_collection.find_one({"_id": user_id})

    # If user not found, raise an exception
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the category exists in the user's list
    categories = user.get("categories_" + task_type, [])
    if category_name not in categories:
        print("This category does not exist in the user's list.")
        return False

        
    # Update the user's list to remove the category
    users_collection.update_one({"_id": user_id}, {"$pull": {"categories_" + task_type: category_name}})

    # Get the tasks collection based on task_type
    tasks_collection = general_tasks_collection if task_type == "general" else schedule_tasks_collection

    # Delete all tasks with the given category and user_id
    result = tasks_collection.delete_many({"user_id": user_id, "category": category_name})

    # If no tasks were deleted, print a message
    if result.deleted_count == 0:
        print("No tasks found for the category", category_name)

    print("Category", category_name, "deleted successfully.")
    return True


def edit_category_name(user_id: str, old_category_name: str, new_category_name: str, task_type: str):
    # Find the user
    user = users_collection.find_one({"_id": user_id})
    if not user:
        raise ValueError("User not found")

    # Check if the old category exists
    old_categories_key = f"categories_{task_type}"
    old_categories = user.get(old_categories_key, [])
    if old_category_name not in old_categories:
        raise ValueError(f"Old category '{old_category_name}' does not exist")

    # Check if the new category name already exists
    new_categories_key = f"categories_{task_type}"
    new_categories = user.get(new_categories_key, [])
    if new_category_name in new_categories:
        return "Category name already exists"

    # Update the category name
    users_collection.update_one(
        {"_id": user_id, f"{old_categories_key}": old_category_name},
        {"$set": {f"{old_categories_key}.$": new_category_name}}
    )

    # Update tasks that belong to the old category
    if task_type == "general":
        general_tasks_collection.update_many(
            {"user_id": user_id, "category": old_category_name},
            {"$set": {"category": new_category_name}}
        )
    elif task_type == "scheduled":
        schedule_tasks_collection.update_many(
            {"user_id": user_id, "category": old_category_name},
            {"$set": {"category": new_category_name}}
        )

    return "Category name updated successfully"


def delete_task(task_id: str, task_type: str, user_id: str, step_index: int = None):
    # Check if the task_type is valid
    if task_type not in ["general", "scheduled"]:
        raise HTTPException(status_code=400, detail="Invalid task type")

    # Convert the task_id string to an ObjectId
    try:
        task_id_obj = ObjectId(task_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid task_id")

    # Get the tasks collection based on task_type
    tasks_collection= general_tasks_collection if task_type == "general" else schedule_tasks_collection

    if step_index is not None:
        # Delete the specific step in the steps array
        task = tasks_collection.find_one({"_id": task_id_obj, "user_id": user_id})
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        if "steps" not in task or not isinstance(task["steps"], list):
            raise HTTPException(status_code=400, detail="Task does not contain steps or steps is not a list")

        if step_index < 0 or step_index >= len(task["steps"]):
            raise HTTPException(status_code=400, detail="Invalid step index")

        # Remove the step at the specified index
        tasks_collection.update_one(
            {"_id": task_id_obj, "user_id": user_id},
            {"$unset": {f"steps.{step_index}": 1}}
        )
        tasks_collection.update_one(
            {"_id": task_id_obj, "user_id": user_id},
            {"$pull": {"steps": None}}
        )

        print("Step removed successfully.")
    else:
        # Delete the task by task_id and user_id
        result = tasks_collection.delete_one({"_id": task_id_obj, "user_id": user_id})

        # If the task is not found, raise an exception
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Task not found")

        print("Task deleted successfully.")


# Update the update_general_task function 
def update_general_task(task_id: str, new_fields: dict, step_index: Optional[int] = None):


    try:
        # Check if task_id is a valid ObjectId
        if not ObjectId.is_valid(task_id):
            raise HTTPException(status_code=400, detail="Invalid task_id")

        # Validate step_index if provided
        if step_index is not None and step_index < 0:
            raise HTTPException(status_code=400, detail="Step index must be non-negative")
            # Convert datetime strings to datetime objects
        for field, value in new_fields.items():
            if field == "duration" and isinstance(value, str):
                # Convert duration string to integer
                new_fields[field] = int(value)

        # Construct the update query
        update_query = {}
        for field, value in new_fields.items():
            if step_index is None:
                # Update task fields
                update_query[field] = value
            else:
                # Update step fields
                update_query[f"steps.{step_index}.{field}"] = value

        # Update the document in the general tasks collection
        result = general_tasks_collection.update_one({"_id": ObjectId(task_id)}, {"$set": update_query})

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="General task not found")

        return "Task updated successfully"
    except HTTPException as e:
        return e


# def update_scheduled_task(task_id: str, new_fields: dict, step_index: Optional[int] = None, update_anyway: bool = False):
#     try:
#         # Check if task_id is a valid ObjectId
#         if not ObjectId.is_valid(task_id):
#             raise HTTPException(status_code=400, detail="Invalid task_id")
#
#         # Validate step_index if provided
#         if step_index is not None and step_index < 0:
#             raise HTTPException(status_code=400, detail="Step index must be non-negative")
#
#         # Convert datetime strings to datetime objects
#         for field, value in new_fields.items():
#             if isinstance(value, str) and field in ["start_time", "end_time", "day_date", "actual_start_time", "actual_end_time"]:
#                 # Remove leading and trailing spaces from the datetime string
#                 value = value.strip()
#                 new_fields[field] = datetime.fromisoformat(value)
#             elif field == "duration" and isinstance(value, str):
#                 # Convert duration string to integer
#                 new_fields[field] = int(value)
#
#         # Check for conflicting tasks if start_time or end_time is updated
#         if "start_time" in new_fields or "end_time" in new_fields:
#             conflicting_tasks = find_conflicting_tasks(new_fields, task_id)
#             if conflicting_tasks and not update_anyway:
#                 return "Task conflicts with existing tasks. Do you want to change the time?"
#
#         # Fetch the existing task
#         task = schedule_tasks_collection.find_one({"_id": ObjectId(task_id)})
#         if not task:
#             raise HTTPException(status_code=404, detail="Scheduled task not found")
#
#         # Ensure steps is an array
#         if 'steps' not in task or not isinstance(task['steps'], list):
#             # Initialize steps as an empty list if it does not exist or is not a list
#             task['steps'] = []
#             # Set the steps field to an empty array in the database
#             schedule_tasks_collection.update_one({"_id": ObjectId(task_id)}, {"$set": {"steps": task['steps']}})
#
#         # Extend the list to accommodate the step_index if necessary
#         if step_index is not None:
#             while len(task['steps']) <= step_index:
#                 task['steps'].append({})
#
#         # Construct the update query
#         update_query = {}
#         for field, value in new_fields.items():
#             if step_index is None:
#                 # Update task fields
#                 update_query.setdefault("$set", {}).update({field: value})
#             else:
#                 # Update step fields
#                 update_query.setdefault("$set", {}).update({f"steps.{step_index}.{field}": value})
#
#         # Update the document in the scheduled tasks collection
#         result = schedule_tasks_collection.update_one({"_id": ObjectId(task_id)}, update_query)
#
#         if result.matched_count == 0:
#             raise HTTPException(status_code=404, detail="Scheduled task not found")
#
#         return "Task updated successfully"
#     except HTTPException as e:
#         return e


def update_scheduled_task(task_id: str, new_fields: dict, step_index: Optional[int] = None,
                          update_anyway: bool = False):
    try:
        # Check if task_id is a valid ObjectId
        if not ObjectId.is_valid(task_id):
            raise HTTPException(status_code=400, detail="Invalid task_id")

        # Validate step_index if provided
        if step_index is not None and step_index < 0:
            raise HTTPException(status_code=400, detail="Step index must be non-negative")

        # Convert datetime strings to datetime objects
        datetime_fields = ["start_time", "end_time", "day_date", "actual_start_time", "actual_end_time"]
        for field, value in new_fields.items():
            if field in datetime_fields and isinstance(value, str):
                # Remove leading and trailing spaces from the datetime string
                value = value.strip()
                new_fields[field] = datetime.fromisoformat(value)
            elif field == "duration" and isinstance(value, str):
                # Convert duration string to integer
                new_fields[field] = int(value)

        # Convert datetime strings to datetime objects in steps if present in new_fields
        if 'steps' in new_fields and isinstance(new_fields['steps'], list):
            for step in new_fields['steps']:
                for field in datetime_fields:
                    if field in step and isinstance(step[field], str):
                        step[field] = datetime.fromisoformat(step[field].strip())

        # Check for conflicting tasks if start_time or end_time is updated
        if "start_time" in new_fields or "end_time" in new_fields:
            conflicting_tasks = find_conflicting_tasks(new_fields, task_id)
            if conflicting_tasks and not update_anyway:
                return "Task conflicts with existing tasks. Do you want to change the time?"

        # Fetch the existing task
        task = schedule_tasks_collection.find_one({"_id": ObjectId(task_id)})
        if not task:
            raise HTTPException(status_code=404, detail="Scheduled task not found")

        # Ensure steps is an array
        if 'steps' not in task or not isinstance(task['steps'], list):
            # Initialize steps as an empty list if it does not exist or is not a list
            task['steps'] = []
            # Set the steps field to an empty array in the database
            schedule_tasks_collection.update_one({"_id": ObjectId(task_id)}, {"$set": {"steps": task['steps']}})

        # Extend the list to accommodate the step_index if necessary
        if step_index is not None:
            while len(task['steps']) <= step_index:
                task['steps'].append({})

        # Construct the update query
        update_query = {}
        for field, value in new_fields.items():
            if step_index is None:
                # Update task fields
                update_query.setdefault("$set", {}).update({field: value})
            else:
                # Update step fields
                update_query.setdefault("$set", {}).update({f"steps.{step_index}.{field}": value})

        # Update the document in the scheduled tasks collection
        result = schedule_tasks_collection.update_one({"_id": ObjectId(task_id)}, update_query)

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Scheduled task not found")

        return "Task updated successfully"
    except HTTPException as e:
        return e
def find_conflicting_tasks(new_fields: dict, task_id: str):
    start_time = new_fields.get("start_time")
    end_time = new_fields.get("end_time")

    if not start_time or not end_time:
        # If either start_time or end_time is not provided, no need to check for conflicts
        return []
    
    # Query for conflicting tasks
    conflicting_tasks = schedule_tasks_collection.find({
        '_id': {'$ne': ObjectId(task_id)},
        '$or': [
            {'start_time': {'$lt': end_time}, 'end_time': {'$gt': start_time}},
            {'start_time': start_time, 'end_time': end_time}
        ]      
    })
    
    # Filter out tasks where start_time is equal to end_time
    conflicting_tasks = [task for task in conflicting_tasks if task['start_time'] != end_time]
    return conflicting_tasks

 