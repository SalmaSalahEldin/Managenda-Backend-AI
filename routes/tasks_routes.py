from datetime import datetime
import sys
from typing import Union
from bson import ObjectId
from fastapi import APIRouter, HTTPException , Body , Query
sys.path.append('D:/Backend/') 
from controllers.tasks_controller import add_category_controller , get_general_tasks_with_category_controller ,get_scheduled_tasks_with_category_controller,add_task_to_category_controller ,delete_category_controller, delete_task_controller , edit_category_name_controller
#from models import TaskResponse, TaskPayload
from models.tasks import GeneralTask_add, ScheduledTask_add,GeneralTask_get, ScheduledTask_get ,TaskResponse ,ScheduledTaskResponse,GeneralTaskResponse, TaskPayload ,TaskPayload2
from models.tasks import update_general_task ,update_scheduled_task 
from models.database import users_collection ,schedule_tasks_collection
router = APIRouter()

@router.post("/add-category/{user_id}/{task_type}")
async def add_category_route(user_id: str, task_type: str, category: str):
    return  add_category_controller(user_id, task_type, category)

@router.get("/get_general_tasks_by_category/{user_id}")
async def get_general_tasks_by_category_route(user_id: str) -> GeneralTaskResponse:
    return  get_general_tasks_with_category_controller(user_id)

@router.get("/get_scheduled_tasks_by_category/{user_id}")
async def get_scheduled_tasks_by_category_route(user_id: str) -> ScheduledTaskResponse:
    return  get_scheduled_tasks_with_category_controller(user_id)

@router.post("/add_task", response_model=str)
async def add_task_route(task_payload: TaskPayload, user_id: str, category: str, task_type: str ,insert_anyway: bool = False):
    return  add_task_to_category_controller(task_payload, user_id, category, task_type,insert_anyway)

@router.delete("/delete-category/{user_id}/{task_type}/{category_name}")
async def delete_category_route(user_id: str, task_type: str, category_name: str):
    try:
        return delete_category_controller(user_id, task_type, category_name)
    except HTTPException as e:
        raise e
    

@router.put("/edit-category/{user_id}/{task_type}/{old_category_name}/{new_category_name}")
async def edit_category_name_route(user_id: str, task_type: str, old_category_name: str, new_category_name: str):
    try:
        return edit_category_name_controller(user_id, old_category_name, new_category_name, task_type)
    except HTTPException as e:
        raise e
    

@router.delete("/delete-task/{task_id}/{task_type}/{user_id}")
async def delete_task_route(task_id: str, task_type: str, user_id: str, step_index: int = Query(None)):
    try:
        return delete_task_controller(task_id, task_type, user_id, step_index)
    except HTTPException as e:
        raise e

@router.put("/general_task/{task_id}")
def update_general_task_fields(task_id: str, new_fields: dict):
    try:
        # Call update_general_task function without specifying a step_index
        response = update_general_task(task_id, new_fields=new_fields)
        return response
    except HTTPException as e:
        return e

@router.put("/general_task/{task_id}/step/{step_index}")
def update_general_task_step(task_id: str, step_index: int, new_fields: dict):
    try:
        # Call update_general_task function with the specified step_index
        response = update_general_task(task_id, new_fields=new_fields, step_index=step_index)
        return response
    except HTTPException as e:
        return e
    

@router.put("/update_scheduled_task/{task_id}")
async def update_scheduled_task_endpoint(task_id: str, new_fields: dict,update_anyway: bool = False ):
    try:
        # Call update_general_task function without specifying a step_index
        response = update_scheduled_task(task_id, new_fields, update_anyway=update_anyway)
        return response
    except HTTPException as e:
        return e

        

@router.put("/scheduled_task/{task_id}/step/{step_index}")
def update_scheduled_task_step(task_id: str, step_index: int, new_fields: dict, update_anyway: bool = False):
    try:
        # Call update_scheduled_task function with the specified step_index
        response = update_scheduled_task(task_id, new_fields=new_fields, step_index=step_index, update_anyway=update_anyway)
        return response
    except HTTPException as e:
        return e
    