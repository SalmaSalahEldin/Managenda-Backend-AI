import sys

from routes import Data_Analysis
sys.path.append('D:/Backend/') 
from fastapi import FastAPI , APIRouter
from routes.users_routes import router as users_router
from routes.notes_routes import router as notes_router
#from routes.schedule_tasks_routes import router as schedule_tasks_router
#from routes.general_tasks_routes import router as general_tasks_router
from routes.tasks_routes import router as tasks_router
from routes.support_routes import router as support_router
from routes.Data_Analysis import router as Data_Analysis
from routes.chatbot_routes import chat_router

app = FastAPI()

# Mount the user routes
app.include_router(users_router, prefix="/users", tags=["users"])

# Mount the note routes
app.include_router(notes_router, prefix="/notes", tags=["notes"])

## Mount the tasks routes
app.include_router(tasks_router, prefix="/tasks", tags=["tasks"])

## Mount the support routes
app.include_router(support_router, prefix="/support-messages", tags=["support-messages"])

## Mount the analysis routes
app.include_router(Data_Analysis, prefix="/analysis", tags=["analysis"])

## Mount the chatbot routes
app.include_router(chat_router, prefix="/chatbot", tags=["chatbot"])
