from fastapi import FastAPI,  Body
#from typing import Optional
from pymongo import MongoClient
from Agent import send_msg

Mongo_URI = "mongodb+srv://Managenda:Graduationproject2024@cluster0.zs4ebry.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(Mongo_URI)

db_name = "Managenda"
collection_name = "schedule_tasks"

MONGODB_COLLECTION = client[db_name][collection_name]

app = FastAPI()

@app.patch('/update/')
async def update(query: dict = Body(...), new_query: dict = Body(...)):
    try:
        MONGODB_COLLECTION.update_one(query,
                                      {"$set": new_query}
                                      )
        return {"status": "ok",
                "messsage": "Your task has been updated successfully"}

    except Exception as e:
        print("An error occurred:", e)


user_id = 'salma'
user_id = [{"role": "assistant", "content": user_id}]

if __name__ == "__main__":
    while True:
        user_input = input("You:  ")
        if user_input.lower() == "exit":
            break

        res = send_msg(user_input, user_id=user_id)
        print("Assistant: ", res["output"])
        print("^^^^^^^^^^^^^^")
        print(res)
        print("__________________")

    # chat_history = []  # Initialize the chat history for the session
    # while True:
    #     user_input = input("You:  ")
    #     if user_input.lower() == "exit":
    #         break
    #
    #     # Send the message and update chat_history
    #     response, chat_history = send_msg(user_input, user_id, chat_history)
    #
    #     # Extract the AI's response to display to the user
    #     ai_response = response.get('output', 'No response generated')
    #
    #     print("Assistant: ", ai_response)
    #     print("^^^^^^^^^^^^^^")
    #     print(response)
    #     print("__________________")

# txt = "For my home workout routine, I start with a warm-up for half an hour, move on to cardio exercises,make sure to hydrate"
# txt = "I want to change the category of the visual communication task to be work"
# res = send_msg(txt)
# print("__________________________________________")
# print(res)
# print("###################")
# print(res["output"])
#
# print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
#
# txt = "exactly"
# res = send_msg(txt)
# print("__________________________________________")
# print(res)
# print("###################")
# print(res["output"])
#
# print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
#
# txt = "Let the category of final2 task job"
# res = send_msg(txt)
# print("__________________________________________")
# print(res)
# print("###################")
# print(res["output"])


