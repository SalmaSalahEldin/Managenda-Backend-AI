import sys

from fastapi import HTTPException
sys.path.append('D:/Backend/') 
from models.users import insert , User , update , delete , get , UpdateUserData


async def create_user(user: User):
    user_dict = user.dict()
    user_dict["_id"] = user_dict.pop("user_id")  # Renaming user_id field to _id for MongoDB
    result = await insert(user_dict)  # Await the coroutine function
    if result and result.acknowledged:
        return "User created successfully"
    else:
        return "Failed to create user"
    



async def update_user(user_id: str, update_data: UpdateUserData):
    # Retrieve user from database based on user_id
    user = await get(user_id) 
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
   # Update user data based on fields provided in update_data
    if update_data.username:
        user['username'] = update_data.username
    if update_data.birth_date is not None:
        user["birth_date"] = update_data.birth_date
    if update_data.avatar:
        user["avatar"] = update_data.avatar
    if update_data.occupation:
        user["occupation"] = update_data.occupation

    # Save updated user data to database
    result = await update(user_id, user)
    if result and result.acknowledged:
        return "User updated successfully"
    else:
        return "Failed to update user"

    


async def delete_user(user_id: str):

    result = await delete(user_id)
    if result and result.deleted_count > 0:
        return "User deleted successfully"
    else:
        return  "Failed to delete user"



async def get_user(user_id: str):
    user = await get(user_id)
    if user:
        return user
    else:
        return "User not found"
    




