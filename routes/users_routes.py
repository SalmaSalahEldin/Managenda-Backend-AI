import sys
sys.path.append('D:/Backend/') 
from fastapi import APIRouter, HTTPException
from models.users import User , UpdateUserData 
from controllers.users_controller import create_user , update_user , delete_user , get_user 
from models.database import users_collection


# it will be needed to edit when we get the id from rassmy 
router = APIRouter()

@router.post("/users/")
async def route_create_user(user: User):
    return await create_user(user)

@router.put("/users/{user_id}")
async def route_update_user(user_id: str, update_data: UpdateUserData):
    return await update_user(user_id, update_data)



@router.delete("/users/{user_id}")
async def route_delete_user(user_id: str):
    return await delete_user(user_id)

@router.get("/users/{user_id}")
async def route_get_user(user_id: str):
    return await get_user(user_id)


