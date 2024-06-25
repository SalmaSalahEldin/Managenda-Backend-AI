import sys
sys.path.append('D:/Backend/') 
from models.schedule_tasks import insert_schedule_task , ScheduleTask

async def create_schedule_task(task: ScheduleTask):
    try:
        # Calculate duration if not provided
        if not task.duration:
            task.duration = task.end_time - task.start_time

        # Calculate actual duration if not provided and actual start and end times are available
        if task.actual_start_time and task.actual_end_time and not task.actual_duration:
            task.actual_duration = (task.actual_end_time - task.actual_start_time)

        # Convert enum to string for storage
        task.status = task.status.value

        # Convert datetime to ISO string for storage
        task_dict = task.model_dump()
        task_dict['start_time'] = task.start_time.isoformat()
        task_dict['end_time'] = task.end_time.isoformat()
        task_dict['day_date'] = task.day_date.isoformat()
        if task.actual_start_time:
            task_dict['actual_start_time'] = task.actual_start_time.isoformat()
        if task.actual_end_time:
            task_dict['actual_end_time'] = task.actual_end_time.isoformat()

        # Convert timedelta to seconds for storage
        if task.duration:
            task_dict['duration'] = task.duration.total_seconds()
        if task.actual_duration:
            task_dict['actual_duration'] = task.actual_duration.total_seconds()

        # Insert task into MongoDB
        result = await insert_schedule_task(task_dict)

        # Check if insertion was successful
        if result.acknowledged:
            # Return response with task details
            inserted_task = {
                **task_dict,
                "_id": str(result.inserted_id)
            }
            return {"message": "Task created successfully", "task": inserted_task}
        else:
            return {"message": "Failed to create task"}
    except Exception as e:
        return {"message": f"Error occurred: {str(e)}"}
