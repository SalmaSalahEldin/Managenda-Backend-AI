import sys
sys.path.append('D:/Backend/')   
from models.notes import Note ,insert_note ,update_note ,delete_note, get_note
    
async def create_note(note: Note):
    result = insert_note(note)  
    if result:
        return {"message": "Note created successfully", "id": str(result)}
    else:
        return {"message": "Failed to create note"}    


    
async def update_note_controller(id: str, updated_fields: dict):
    try:
        result = await update_note(id, updated_fields)  # Call the update_note function directly
        if result:
            return {"message": "Note updated successfully"}
        else:
            return {"message": "Failed to update note"}
    except Exception as e:
        # Log the error for debugging purposes
        print(f"Error updating note: {str(e)}")
        return {"message": "Failed to update note"}

 
async def delete_note_controller(id: str):
    try:
        result = await delete_note(id)  # Call the delete_note function directly
        if result:
            return {"message": "Note deleted successfully"}  
        else:
            return {"message": "Failed to delete note"}  # Indicate failed deletion
    except Exception as e:
        # Log the error for debugging purposes
        print(f"Error deleting note: {str(e)}")
        return {"message": "Failed to delete note"}  # Indicate failed deletion
    

async def get_note_controller(id: str):
    note = get_note(id)
    if note:
        return note.dict()
    else:
        return {"message": "Note not found"}

