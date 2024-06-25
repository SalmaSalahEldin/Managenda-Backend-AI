import sys
from typing import Union
from fastapi import HTTPException
from fastapi.responses import JSONResponse ,PlainTextResponse
sys.path.append('D:/Backend/') 
from models.tasks import add_category, get_general_tasks_with_category,get_scheduled_tasks_with_category, add_task_to_category , delete_category , delete_task  , edit_category_name
from models.tasks import GeneralTask_get, ScheduledTask_get ,TaskResponse , TaskPayload ,GeneralTask_add , ScheduledTask_add ,TaskPayload2



def add_category_controller(user_id: str, task_type: str, category: str):
    try:
        category_added = add_category(user_id, task_type, category)
        if category_added:
            return "Category added successfully"
        else:
            return "Category already exists"
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


def get_general_tasks_with_category_controller(user_id: str):
    try:
        categorized_tasks = get_general_tasks_with_category(user_id)
        return categorized_tasks
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
def get_scheduled_tasks_with_category_controller(user_id: str):
    try:
        categorized_tasks = get_scheduled_tasks_with_category(user_id)
        return categorized_tasks
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
def add_task_to_category_controller(task_payload: TaskPayload, user_id: str, category: str, task_type: str, insert_anyway: bool = False):
    try:
        response = add_task_to_category(task_payload, user_id, category, task_type, insert_anyway)
        
        if isinstance(response, dict):
            # If the response is a dictionary, it means there was a conflict or some other issue
            # Return the message from the response
            return response["message"]
        else:
            # If the response is not a dictionary, it means the task was inserted successfully
            return "Task inserted successfully!"
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to insert task: " + str(e))

def delete_category_controller(user_id: str, task_type: str, category_name: str):
    if category_name == "un_categorized":
        raise HTTPException(status_code=400, detail="This category cannot be deleted.")
    try:
        if delete_category(user_id, task_type, category_name):
            return "Category deleted successfully"
        else:
            raise HTTPException(status_code=404, detail="Category not found")
    except HTTPException as e:
        raise e
    

def edit_category_name_controller(user_id: str, old_category_name: str, new_category_name: str, task_type: str):
    try:
        result = edit_category_name(user_id, old_category_name, new_category_name, task_type)
        if result == "Category name updated successfully":
            return PlainTextResponse(content=f'"{result}"', status_code=200)
        elif result == "Category name already exists":
            return PlainTextResponse(content=f'"{result}"', status_code=200)
    except ValueError as e:
        return PlainTextResponse(content=f'"{str(e)}"', status_code=400)
    except Exception as e:
        return PlainTextResponse(content='"Internal Server Error"', status_code=500)

def delete_task_controller(task_id: str, task_type: str, user_id: str, step_index: int = None):
    try:
        delete_task(task_id, task_type, user_id, step_index)
        if step_index is not None:
            return JSONResponse(status_code=200, content= "Step removed successfully")
        else:
            return JSONResponse(status_code=200, content= "Task deleted successfully")
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})

    
#def update_task_controller(task_id: str, task_type: str, task_data: TaskPayload2, update_anyway: bool = False):
    #try:
        #response = update_task(task_id, task_type, task_data, update_anyway)
        
        #if isinstance(response, dict):
            # If the response is a dictionary, it means there was a conflict or some other issue
            # Return the message from the response
            #return response["message"]
        #else:
            # If the response is not a dictionary, it means the task was updated successfully
            #return "Task updated successfully!"
    #except HTTPException as e:
        #raise e
    
    #except Exception as e:
        #raise HTTPException(status_code=500, detail="Failed to update task: " + str(e))
        



    