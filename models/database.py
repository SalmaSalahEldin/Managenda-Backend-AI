from pymongo import MongoClient

# Connect to MongoDB Atlas
client = MongoClient("mongodb+srv://Managenda:Graduationproject2024@cluster0.zs4ebry.mongodb.net/")
db = client["Managenda"]
users_collection = db["users"]
notes_collection = db["notes"]
schedule_tasks_collection = db["schedule_tasks"]
general_tasks_collection = db["general_tasks"]
support_collection = db["support"]

