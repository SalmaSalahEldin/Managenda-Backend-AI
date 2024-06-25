""" # Function to calculate morning_evening_percentage
def calculate_task_completion_percentage(user_id: str, input_date: datetime.date, timeframe: str):
    if timeframe == "weekly":
        return None

    # Define morning and evening time ranges
    morning_start_time = datetime.strptime("06:00", "%H:%M").time()
    morning_end_time = datetime.strptime("15:00", "%H:%M").time()
    evening_start_time = datetime.strptime("15:01", "%H:%M").time()
    evening_end_time = datetime.strptime("23:59", "%H:%M").time()

    # Get tasks for the user for the specified date
    tasks = schedule_tasks_collection.find({
        "user_id": user_id,
        "end_time": {
            "$gte": datetime.combine(input_date, datetime.min.time()),
            "$lt": datetime.combine(input_date + timedelta(days=1), datetime.min.time())
        }
    })

    # Initialize counts for tasks completed in morning and evening hours
    morning_tasks_completed = 0
    evening_tasks_completed = 0
    total_tasks = 0

    # Count tasks completed in morning and evening hours
    for task in tasks:
        if task.get("task_status") == "completed":
            total_tasks += 1
            start_time = task["start_time"].date()
            end_time = task["end_time"].date()
            # Check if the task falls within morning hours
            if morning_start_time <= start_time <= morning_end_time or morning_start_time <= end_time <= morning_end_time:
                morning_tasks_completed += 1
            # Check if the task falls within evening hours
            elif evening_start_time <= start_time <= evening_end_time or evening_start_time <= end_time <= evening_end_time:
                evening_tasks_completed += 1

    # Calculate the percentage of tasks completed in morning and evening hours
    total_morning_percentage = (morning_tasks_completed / total_tasks) * 100 if total_tasks > 0 else 0
    total_evening_percentage = (evening_tasks_completed / total_tasks) * 100 if total_tasks > 0 else 0

    return total_morning_percentage, total_evening_percentage


            # Calculate task completion percentage
        morning_evening_percentage = calculate_task_completion_percentage(user_id, input_date, timeframe)

        # Check if morning_evening_percentage is not None before accessing its elements
        if morning_evening_percentage is not None:
            morning_percentage, evening_percentage = morning_evening_percentage
        else:
            morning_percentage, evening_percentage = None, None
            "morning_evening_percentage": {
                "morning": morning_percentage,
                "evening": evening_percentage
            }, """

""" def calculate_productivity_score(user_id: str, input_date: datetime.date, timeframe: str):
    # Define start and end dates based on timeframe
    if timeframe == "daily":
        start_date = datetime.combine(input_date, datetime.min.time())
        end_date = start_date + timedelta(days=1)
    elif timeframe == "weekly":
        start_date = datetime.combine(input_date, datetime.min.time())
        end_date = start_date + timedelta(days=7)
    else:
        raise HTTPException(status_code=400, detail="Invalid timeframe. Use 'daily' or 'weekly'.")

    # Get all tasks for the user within the given timeframe
    tasks = schedule_tasks_collection.find({
        "user_id": user_id,
        "$or": [
            {"end_time": {"$gte": start_date, "$lt": end_date}},  # Tasks with end time within range
            {"start_time": {"$gte": start_date, "$lt": end_date}},  # Tasks with start time within range
            {"actual_end_time": {"$gte": start_date, "$lt": end_date}}  # Completed tasks within range
        ]
    })

    total_tasks = 0
    completed_tasks = 0
    task_ids = []

    # Count total and completed tasks
    for task in tasks:
        include_task = True

        # Check if actual_start_time exists and falls outside the timeframe
        if "actual_start_time" in task:
            actual_start_time = task["actual_start_time"]
            if actual_start_time < start_date or actual_start_time >= end_date:
                include_task = False

        # Check if actual_end_time exists and falls outside the timeframe
        if "actual_end_time" in task:
            actual_end_time = task["actual_end_time"]
            if actual_end_time.date() == input_date:
                include_task = False

        # Ensure the task has start_time and end_time within the timeframe if actual times are absent
        if "start_time" in task and "end_time" in task:
            start_time = task["start_time"]
            end_time = task["end_time"]
            if start_time < start_date or start_time >= end_date or end_time < start_date or end_time >= end_date:
                include_task = False

        if include_task:
            # Increment total_tasks for each task found within the timeframe
            total_tasks += 1
            task_ids.append(str(task["_id"]))  # Convert ObjectId to string

            # Check for tasks with both end_time and actual_end_time within the timeframe
            if "end_time" in task and "actual_end_time" in task:
                end_time = task["end_time"]
                actual_end_time = task["actual_end_time"]
                if start_date <= end_time < end_date and start_date <= actual_end_time < end_date:
                    completed_tasks += 1        
            # Check for tasks with start_time and actual_start_time within the timeframe
            elif "start_time" in task and "actual_start_time" in task:
                start_time = task["start_time"]
                actual_start_time = task["actual_start_time"]
                if start_date <= start_time < end_date and start_date <= actual_start_time < end_date:
                    completed_tasks += 1        
            # Check for tasks with only actual_end_time within the timeframe
            elif "actual_end_time" in task:
                actual_end_time = task["actual_end_time"]
                if start_date <= actual_end_time < end_date:
                    completed_tasks += 1

    # Calculate productivity score
    productivity_score = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0

    return {
        "productivity_score": productivity_score,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "task_ids": task_ids  # Return the list of task IDs as strings
    }

 """

""""""
"""

def get_tasks_completion_ratio(user_id: str, date: datetime, timeframe: str):

    # Convert date string to datetime object
    query_date = datetime.combine(date, datetime.min.time())

    # Define start and end date based on timeframe
    if timeframe == "daily":
        start_date = query_date
        end_date = query_date + timedelta(days=1)
    elif timeframe == "weekly":
        start_date = query_date
        end_date = query_date + timedelta(days=7)
    else:
        raise HTTPException(status_code=400, detail="Invalid timeframe. Use 'daily' or 'weekly'.")

    # Define the query based on tasks falling within the specified date range
    query = {
        "user_id": user_id,
        "$or": [
            {"start_time": {"$gte": start_date, "$lt": end_date}, "actual_start_time": {"$exists": True}},
            {"end_time": {"$gte": start_date, "$lt": end_date}, "actual_end_time": {"$exists": True}}
        ]
    }

    tasks = schedule_tasks_collection.find(query)
    
    total_completed_tasks = 0
    on_time_tasks = 0
    early_tasks = 0
    delay_tasks = 0

    for task in tasks:
        total_completed_tasks += 1

        # Check if the task is on time, early, or delayed based on available fields
        if "actual_start_time" in task and "actual_end_time" in task:
            actual_start_time = task["actual_start_time"]
            actual_end_time = task["actual_end_time"]
            if actual_end_time == task.get("end_time") and actual_start_time == task.get("start_time"):
                on_time_tasks += 1
            elif actual_end_time < task.get("end_time"):
                early_tasks += 1
            else:
                delay_tasks += 1
        elif "actual_end_time" in task:
            actual_end_time = task["actual_end_time"]
            if actual_end_time == task.get("end_time"):
                on_time_tasks += 1
            elif actual_end_time < task.get("end_time"):
                early_tasks += 1
            else:
                delay_tasks += 1
        elif "actual_start_time" in task:
            actual_start_time = task["actual_start_time"]
            if actual_start_time == task.get("start_time"):
                on_time_tasks += 1
            elif actual_start_time < task.get("start_time"):
                early_tasks += 1
            else:
                delay_tasks += 1

    return {
        "total_completed_tasks": total_completed_tasks,
        "on_time_tasks": on_time_tasks,
        "early_tasks": early_tasks,
        "delay_tasks": delay_tasks
    }

"""

"""
        # Calculate completion ration
        completion_ratio = get_tasks_completion_ratio(user_id, input_date, timeframe)
            "completion_ratio": completion_ratio,

"""