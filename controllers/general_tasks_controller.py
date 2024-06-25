import sys
sys.path.append('D:/Backend/') 
from models.general_tasks import insert_general_task , GeneralTask 

async def  create_general_task(general_task_dict: dict):
    result = await insert_general_task(general_task_dict)
    if result.acknowledged:
        inserted_task = {
            **general_task_dict,
            "_id": str(result.inserted_id)
        }
        return {"message": "General task created successfully", "task": inserted_task}
    else:
        return {"message": "Failed to create general task"}

async def handle_create_general_task(task: GeneralTask):
    # Calculate total duration
    total_duration = sum(step.duration for step in task.steps)
    
    # Prepare task dictionary
    general_task_dict = task.model_dump()
    general_task_dict['total_duration'] = total_duration
    
    # Create general task
    return  await create_general_task(general_task_dict)
