import sys
sys.path.append('D:/Backend/') 
from fastapi import APIRouter, BackgroundTasks, HTTPException
from models.support import Support
from controllers.support_controller import get_support_messages_controller , insert_support_messages_controller

router = APIRouter()

@router.post("/support-messages/")
async def insert_support_message(support: Support, background_tasks: BackgroundTasks):
    response = await insert_support_messages_controller(support)
    return response

@router.get("/support-messages/{user_id}")
def get_support_messages(user_id: str):
    return get_support_messages_controller(user_id)
