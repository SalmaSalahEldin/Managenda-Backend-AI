from Chatbot.Agent import send_msg
from models.chatbot import ChatRequest
from fastapi import APIRouter, Query, HTTPException, FastAPI
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse

chat_router = APIRouter()

@chat_router.post("/chatbot/{user_id}")
async def chat_endpoint(user_id: str , text: str ):
    try:
        response = send_msg(text, user_id)

        final_output_response = response.get("response", "No response available")
        final_output_data = response.get("data", {})

        return JSONResponse(content={
            "response": final_output_response,
            "data": final_output_data
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





# @chat_router.post("/chat")
# async def chat_endpoint(request: ChatRequest):
#     try:
#         response = send_msg(request.text, request.user_id)
#
#         final_output = response.get("output", "No response available")
#         return {"response": final_output}
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
#


# @chat_router.post("")
# async def chat_endpoint(user_id: str = Query(...), text: str = Query(...)):
#     try:
#         response = send_msg(text, user_id)
#
#         # Extract the "output" field from the response
#         final_output = response.get("output", "No response available")
#         final_output = final_output.strip().replace("```json", "").replace("```", "").replace("\\n", "").replace("\\", "").replace("{", "").replace("}", "").replace("\"", "").replace(":", "").replace(",", " ").replace("\n\n", " ")
#
#         return {"response": final_output}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
