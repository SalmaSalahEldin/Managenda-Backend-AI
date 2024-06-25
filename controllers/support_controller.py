import sys
from bson import ObjectId
from fastapi import HTTPException
sys.path.append('D:/Backend/') 
from models.support import Support, insert_support_messages, get_support_messages
from email_client import send_email
from models.users import users_collection

async def insert_support_messages_controller(support: Support):
    # Retrieve user's name from users collection
    user = users_collection.find_one({"_id": support.user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_name = user.get("username", "User")  # Default to "User" if username is not found

    result = insert_support_messages(support)
    if result:
        subject = "Support Message Received"
        email_to = support.email
        body = f"""
        <h1>Support Message Received</h1>
        <p>Dear {user_name},</p>
        <p>Thank you for reaching out to us. We have received your message and will get back to you shortly.</p>
        <p>Best Regards,</p>
        <p>Your Support Team</p>
        """
        await send_email(subject, email_to, body)
        return {"message": "Message sent successfully. We will reach you soon", "id": str(result.inserted_id)}
    else:
        return {"message": "Failed to send message"}
    
    
def get_support_messages_controller(user_id: str):
    supports = get_support_messages(user_id)
    if not supports:
        raise HTTPException(status_code=404, detail="No support messages found for the user")
    return supports
