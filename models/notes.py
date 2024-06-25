import sys
sys.path.append('D:/Backend/') 
from datetime import datetime
from pydantic import BaseModel
from models.database import notes_collection
from bson import ObjectId  # Import ObjectId from bson

class Note(BaseModel):
    user_id: str
    title: str
    content: str
    creation_date: datetime = None
    updated_date: datetime = None

def insert_note(note: Note):
    note.creation_date = datetime.now()
    note_dict = note.dict()
    return notes_collection.insert_one(note_dict)
    
def update_note(note_id: str, updated_data: dict):

    # Set the updated date to the current time
    updated_data['updated_date'] = datetime.now()

    # Perform the update operation
    result = notes_collection.update_one(
        {"_id": ObjectId(note_id)},
        {"$set": updated_data}
    )

    # Check if the update was successful
    if result.modified_count == 1:
        return True
    else:
        return False
    


def delete_note(note_id: str):
    # Perform the delete operation
    return notes_collection.delete_one({"_id": ObjectId(note_id)})

def get_note(note_id: str):
    # Retrieve the note from the database
    note_data = notes_collection.find_one({"_id": ObjectId(note_id)})

    # If note_data is None, no note with the provided ID was found
    if note_data is None:
        return None
    # Convert the retrieved data to a Note instance
    note = Note(**note_data)

    return note   