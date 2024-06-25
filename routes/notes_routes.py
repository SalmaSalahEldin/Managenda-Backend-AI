import sys
sys.path.append('D:/Backend/') 
from fastapi import APIRouter
from models.notes import Note
from controllers.notes_controller import create_note, get_note_controller ,delete_note_controller ,update_note_controller

router = APIRouter()

@router.post("/notes/")
async def route_create_note(note: Note):
    return await create_note(note)

@router.put("/notes/{id}")
async def route_update_note(id: str, updated_fields: dict):
    result = await update_note_controller(id, updated_fields)
    if result:
        return {"message": "Note updated successfully"}
    else:
        return {"message": "Failed to update note"}


@router.delete("/notes/{id}")
async def route_delete_note(id: str):
    result = await delete_note_controller(id)
    if result:
        return {"message": "Note deleted successfully"}
    else:
        return {"message": "Failed to delete note"}

@router.get("/notes/{id}")
async def route_get_note(id: str):
    return await get_note_controller(id)