import requests.exceptions
import urllib.error
from fastapi import HTTPException
# from Chatbot import Constants
import requests.exceptions
import urllib.error
import requests.exceptions
import urllib.error
from langchain.chat_models import ChatOpenAI
from pymongo import MongoClient, errors
import requests.exceptions
import urllib.error
from idlelib.iomenu import errors
from langchain.adapters import openai
from datetime import datetime,timedelta,timezone
import requests.exceptions
import urllib.error
from Chatbot import SelfQuery, Constants
import ast
from openai import OpenAIError
from langchain.tools import StructuredTool
import datetime
import requests.exceptions
import urllib.error
#from langchain.chat_models import ChatOpenAI
from openai import OpenAI
from pymongo import MongoClient
from langchain.schema import Document
import os
from langchain_experimental.text_splitter import SemanticChunker
from openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator, root_validator
import requests
import logging
import json
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import UnstructuredFileLoader
import re
from controllers.tasks_controller import add_task_to_category_controller
from models.tasks import TaskPayload, Step_add, ScheduledTask_add, GeneralTask_add, Step_general, update_general_task, update_scheduled_task
import openai
from openai import OpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# model = ChatOpenAI(
#     temperature=0.2,
#     model='gpt-3.5-turbo-0125',
# )


os.environ["OPENAI_API_KEY"] = "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"
client = OpenAI(api_key="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")
os.environ["PINECONE_API_KEY"] = "da2b64b9-04d6-4ac3-b075-a242f4755479"
embeddings = OpenAIEmbeddings()


# Define models
class GeneralTaskSchema(BaseModel):
    task_name: str = Field(description="The main task name that the user wants to perform")
    steps: str = Field(description="The steps mentioned in the text that should be done prior to the main task")
    category: Optional[str] = Field("Un-categorized", min_length=1,
                                    description="The category of the main task. ONLY IF the user has inputted it")
    user_id: str = Field(min_length=1, description="The ID of the user. This field is always required, DON'T ever generate a user_id by yourself. Always take this argument from agent's arguments.")
    insert_anyway: bool = Field(False,
                                description="Regardless of the existence of an old task scheduled for the same start time, the user may choose to insert their task anyway.")

class Step(BaseModel):
    step_name: str
    duration: int  # In minutes

class GeneralTask(BaseModel):
    task_name: str
    steps: List[Step]

def parse_steps(steps_json: Dict[str, List[str]]) -> List[Step]:
    steps = []
    if not steps_json or all(not step_name for step_name in steps_json.keys()):
        return []

    for step_key, details in steps_json.items():
        # Skip keys that do not follow the "Step" pattern
        if not step_key.lower().startswith("step"):
            continue

        duration_str = details[1]
        if duration_str.lower() == "none":
            duration = 0
        else:
            hours, minutes, seconds = map(int, duration_str.split(':'))
            duration = hours * 60 + minutes  # convert hours and minutes to total minutes

        steps.append(Step(step_name=details[0], duration=duration))

    return steps

def general_task(task_name, steps, user_id, category, task_type='general', insert_anyway=False):
    print('general_task function called')
    print(f'Arguments received: task_name={task_name}, steps={steps}, user_id={user_id}, category={category}, category_name={category}, task_type={task_type}, insert_anyway={insert_anyway}')

    try:
        print('Entered try block')
        model = ChatOpenAI(temperature=0.2, model='gpt-3.5-turbo-0125', streaming=False)

        _json = model.predict(
            "You will take a category of the main task, task name and its steps with duration. "
            "DON'T ASSUME THE CATEGORY AND LEAVE IT None IF THE USER DIDN'T MENTION IT. "
            "Extract the category of the main task, task name and the steps with their duration and return them in a JSON object. "
            "If there's a duration not mentioned for a step, put None as its duration. "
            "Example: without mentioned category \n"
            "Task name: Do the laundry\n"
            "Steps with duration: 1) Put the clothes in the washing machine\n"
            "2) Put the washing liquid 1.3 hours\n"
            "3) Turn on the washing machine 3 min\n"
            "4) Turn it off 0 sec\n"
            "Json:\n"
            "{\n"
            "    \"Category\": \"Un-categorized\",\n"
            "    \"task_name\": \"Do the laundry\",\n"
            "    \"Steps\": {\"Step 1\": [\"Put the clothes in the washing machine\", \"None\"],\n"
            "              \"Step 2\": [\"Put the washing liquid\", \"01:18:00\"],\n"
            "              \"Step 3\": [\"Turn on the washing machine\", \"00:03:00\"],\n"
            "              \"Step 4\": [\"Turn it off\", \"00:00:00\"]\n"
            "    }\n"
            "}\n\n"
            "Example: with mentioned category\n"
            "I have an online meeting under the meetings category: Bring notebook, Charge laptop for 1h, prepare slides 30m\n"
            "Json:\n"
            "{\n"
            "    \"Category\": \"meetings\",\n"
            "    \"task_name\": \"Online Meeting\",\n"
            "    \"Steps\": {\"Step 1\": [\"Bring notebook\", \"None\"],\n"
            "              \"Step 2\": [\"Charge laptop\", \"01:00:00\"],\n"
            "              \"Step 3\": [\"Prepare slides\", \"00:30:00\"]\n"
            "    }\n"
            "}\n\n"
            "Here is the task name and its steps:\n"
            f"category: {category.lower()}\n"
            f"Task name: {task_name.lower()}\n"
            f"Steps: {steps}\n\n"
        )

        print('Received JSON response from model')
        _json = _json[_json.find("{"):_json.rfind("}") + 1]
        _json = json.loads(_json)

        steps_parsed = parse_steps(_json.get("Steps", {}))
        if not steps_parsed:
            steps_parsed = []

        general_task_add = GeneralTask_add(
            task_name=_json["task_name"],
            steps=[Step_general(step_name=step.step_name, duration=step.duration) for step in steps_parsed]
        )

        print("general_task_add")
        print(general_task_add)

        task_payload = TaskPayload(general_task=general_task_add, schedule_task=None)

        response = add_task_to_category_controller(task_payload, user_id, category, task_type, insert_anyway)

        if response == "Task conflicts with existing tasks":
            return {
                "response": "You currently have another task scheduled for the same time. Would you prefer to insert this task anyway or choose a different time for this task?",
                "data": {}
            }

        return {
            "response": response,
            "data": task_payload.dict()
        }

    except ValueError as ve:
        print(f"Error parsing JSON: {ve}")
        return {
            "response": "My apologies, can you send your request again",
            "data": {}
        }

    except openai.APIConnectionError as e:
        print(f"OpenAI API request failed to connect: {e}")
        return {
            "response": "Failed to connect to OpenAI API",
            "data": {}
        }

def get_general_task_tool():
    return StructuredTool(
        name="general_task",
        description="Use this tool when the user enters a sequence of steps for a task and you want to save the steps with the task name and the duration if found.",
        func=general_task,
        args_schema=GeneralTaskSchema,
    )















# without model.predict (without response formatting)

class StepForSchedule(BaseModel):
    step_name: str
    start_time: str
    end_time: str

    @root_validator(pre=True)
    def format_datetimes(cls, values):
        start_date = values.get('start_date', datetime.now().strftime('%Y-%m-%d'))

        for field_name in ['start_time', 'end_time']:
            value = values.get(field_name)
            if value and 'T' not in value:
                try:
                    formatted_value = datetime.strptime(f"{start_date} {value}", "%Y-%m-%d %H:%M").strftime(
                        "%Y-%m-%dT%H:%M:%S.%fZ")
                    values[field_name] = formatted_value
                except ValueError:
                    formatted_value = datetime.strptime(f"{start_date} {value}", "%Y-%m-%d %I:%M %p").strftime(
                        "%Y-%m-%dT%H:%M:%S.%fZ")
                    values[field_name] = formatted_value

        return values

    @validator('start_time', 'end_time', pre=True)
    def check_format(cls, value):
        if isinstance(value, str):
            try:
                datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
            except ValueError:
                raise ValueError("Datetime format should be 'YYYY-MM-DDTHH:MM:SS.ssssssZ'")
        return value

class ScheduledTask(BaseModel):
    task_name: str = Field(..., min_length=1, description="Name of the task according to what the user writes")
    steps: List[StepForSchedule] = Field(..., description="List of steps that this task consists of")
    start_time: str = Field(..., description="The start time of this task according to what the user writes")
    end_time: str = Field(..., description="The end time of this task according to what the user writes")

    @root_validator(pre=True)
    def format_datetimes(cls, values):
        date = values.get('date', datetime.now().strftime('%Y-%m-%d'))

        for field_name in ['start_time', 'end_time']:
            value = values.get(field_name)
            if value and 'T' not in value:
                try:
                    formatted_value = datetime.strptime(f"{date} {value}", "%Y-%m-%d %H:%M").strftime(
                        "%Y-%m-%dT%H:%M:%S.%fZ")
                    values[field_name] = formatted_value
                except ValueError:
                    formatted_value = datetime.strptime(f"{date} {value}", "%Y-%m-%d %I:%M %p").strftime(
                        "%Y-%m-%dT%H:%M:%S.%fZ")
                    values[field_name] = formatted_value

        return values

    @validator('start_time', 'end_time', pre=True)
    def check_format(cls, value):
        if isinstance(value, str):
            try:
                datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
            except ValueError:
                raise ValueError("Datetime format should be 'YYYY-MM-DDTHH:MM:SS.ssssssZ'")
        return value

class ScheduleTaskToolSchema(BaseModel):
    task_name: str = Field(
        ...,
        min_length=1,
        description="Name of the task according to what the user writes",
    )
    date: Optional[str] = Field(
        None,
        description="Date of the task only if the user inputs it"
    )
    start_time: Optional[str] = Field(
        None,
        description="Start time of the task only if the user inputs it. Leave empty if the user didn't input it",
    )
    end_time: Optional[str] = Field(
        None,
        description="End time of the task only if the user inputs it. Leave empty if the user didn't input it",
    )
    end_date: Optional[str] = Field(
        "null", min_length=1,
        description="The date on which the user intends to complete or terminate their task. This date signifies the final day that the task is"
                    "expected to be active, ONLY if the user inputs it."
                    "For example, if a user has a task starting on the 1st of July and plans to complete it by the 5th of July, the end_date will be the 5th of July."
    )
    category: Optional[str] = Field(
        "Un-categorized",
        description="The category of the task.ONLY IF the user has inputted it. Leave it Un-categorized if the user didn't input it explicitly",
    )
    steps: List[StepForSchedule] = Field(
        default_factory=list,
        description="Detailed steps involved in completing the task, each with a specified start and end time."
    )

def insert_schedule_task_to_mongodb(task_data, user_id='salma', category="work", task_type='scheduled', insert_anyway=True):
    steps = [
        StepForSchedule(
            step_name=step['step_name'],
            start_time=step['start_time'],
            end_time=step['end_time']
        )
        for step in task_data['schedule_task']['steps']
    ]

    # task_payload = {
    #     "schedule_task": {
    #         "task_name": task_data['schedule_task']['task_name'],
    #         "steps": steps,
    #         "start_time": task_data['schedule_task']['start_time'],
    #         "end_time": task_data['schedule_task']['end_time']
    #     }
    # }

    task_payload = {
            "task_name": task_data['schedule_task']['task_name'],
            "steps": steps,
            "start_time": task_data['schedule_task']['start_time'],
            "end_time": task_data['schedule_task']['end_time']
    }

    print("task_payload")

    print(task_payload)

    task_payload = TaskPayload(schedule_task=task_payload, general_task=None)


    try:
        response = add_task_to_category_controller(task_payload, user_id=user_id, category=category, task_type=task_type, insert_anyway=insert_anyway)
        answer = response
    except HTTPException as e:
        logger.error(f"Failed to insert scheduled task into MongoDB: {e.detail}")
        answer = f'Failed to insert scheduled task into MongoDB. Error: {e.detail}'
    except Exception as e:
        logger.error(f"An exception occurred while inserting the task: {e}")
        answer = f'An exception occurred while inserting the task: {e}'

    result = {
        "response": answer,
        "data": task_data
    }

    print("Result:")
    print(result)

    return result

def parse_steps_for_scheduled(steps_json: List[Dict[str, str]], date: str) -> List[StepForSchedule]:
    steps = []

    if steps_json is not None:
        for step in steps_json:
            step_dict = step if isinstance(step, dict) else step.dict()
            step_dict = {k.lower().replace(' ', '_'): v for k, v in step_dict.items()}  # Normalize keys
            step_name = step_dict['step_name']
            if 'T' in step_dict['start_time']:
                start_time = step_dict['start_time']
            else:
                try:
                    start_time = f"{date}T{datetime.strptime(step_dict['start_time'], '%H:%M').strftime('%H:%M:%S.%fZ')}"
                except ValueError:
                    start_time = f"{date}T{datetime.strptime(step_dict['start_time'], '%I:%M %p').strftime('%H:%M:%S.%fZ')}"
            if 'T' in step_dict['end_time']:
                end_time = step_dict['end_time']
            else:
                try:
                    end_time = f"{date}T{datetime.strptime(step_dict['end_time'], '%H:%M').strftime('%H:%M:%S.%fZ')}"
                except ValueError:
                    end_time = f"{date}T{datetime.strptime(step_dict['end_time'], '%I:%M %p').strftime('%H:%M:%S.%fZ')}"
            steps.append(
                StepForSchedule(step_name=step_name, start_time=start_time, end_time=end_time))
    return steps

def schedule_task(task_name, steps=None, category="Un-categorized", date=None, start_time=None, end_time=None,
                  end_date="null"):

    logger.info("Entered Scheduled task tool")
    if start_time is None and end_time is None:
        return "Both start and end times are missing. Please enter a start time and end time."
    elif end_time is None:
        return "End time is missing. Please enter an end time."
    elif start_time is None:
        return "Start time is missing. Please enter a start time."

    date = date or datetime.now().strftime('%Y-%m-%d')

    if 'T' in start_time:
        start_time_dt = start_time
    else:
        try:
            start_time_dt = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M").strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            start_time_dt = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %I:%M %p").strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    if 'T' in end_time:
        end_time_dt = end_time
    else:
        try:
            end_time_dt = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M").strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            end_time_dt = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %I:%M %p").strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    steps_parsed = parse_steps_for_scheduled(steps if steps is not None else [], date)

    scheduled_task = ScheduledTask(
        task_name=task_name,
        steps=steps_parsed,
        start_time=start_time_dt,
        end_time=end_time_dt
    )

    task_data = {
        "schedule_task": {
            "task_name": scheduled_task.task_name,
            "steps": [step.dict() for step in scheduled_task.steps],
            "start_time": scheduled_task.start_time,
            "end_time": scheduled_task.end_time,
        }
    }

    if "steps" in task_data['schedule_task']:
        end_time_updated = False
        for step in task_data['schedule_task']["steps"]:
            if not end_time_updated:
                start = step["start_time"]
                end = step["end_time"]

                start_iso = datetime.fromisoformat(start.replace('Z', '+00:00'))
                end_iso = datetime.fromisoformat(end.replace('Z', '+00:00'))

                if end_iso < start_iso:
                    end_time_only = end.split("T")[1]
                    if end_date:
                        end = f"{end_date}T{end_time_only}"
                    else:
                        end_iso += timedelta(days=1)
                        next_date = str(end_iso).split(" ")[0]
                        end = f"{next_date}T{end_time_only}.000Z"

                    end_time_updated = True
                    step["end_time"] = end

    logger.info(f"Task data: {task_data}")
    return insert_schedule_task_to_mongodb(task_data, user_id='salma', category=category)

def get_schedule_task_tool():
    return StructuredTool(
        name="schedule_task",
        description="Use this tool to save the category of the task, task name, date, start time, and end time of the task if the user enters them.",
        func=schedule_task,
        args_schema=ScheduleTaskToolSchema,
    )










class SetReminderToolSchema(BaseModel):
    reminder_name: str = Field(
        ...,
        min_length=1,
        description="Name of the reminder according to what the user writes",
    )
    date: str = Field(
        None, min_length=1, description="Date of the reminder only if the user inputs it"
    )
    time: str = Field(
        None,
        min_length=0,
        description="Time of the reminder only if the user inputs it. Leave empty if the user didn't input it",
    )
    category: Optional[str] = Field(
        "Un-categorized",
        description="The category of the task. ONLY IF the user has inputted it. Leave it Un-categorized if the user didn't input it explicitly",
    )
    user_id: str = Field(min_length=1,
         description="The ID of the user. This field is always required, DON'T ever generate a user_id by yourself. Always take this argument from agent's arguments."
    )
    insert_anyway: bool = Field(False,
         description="Regardless of the existence of an old task scheduled for the same start time, the user may choose to insert their task anyway."
    )

def set_reminder_tool(reminder_name, user_id, date=None, time=None, category="un-categorized", insert_anyway=False):
    if time is None:
        return {
            "response": "Time is missing.",
            "data": {}
        }

    current_datetime = datetime.now()
    current_date = current_datetime.date()
    current_time_plus_2_hours = current_datetime + timedelta(hours=2)
    current_day = current_datetime.strftime('%A')

    model = ChatOpenAI(
        temperature=0.2,
        model='gpt-3.5-turbo-0125',
    )
    _json = model.predict(
        "Given the following input from the user, please extract that the appointment parameters below.\n"
        + f"Assume today's date is {current_date} and current time is {current_time_plus_2_hours} and today's day is {current_day}.\n"
        + "Extract date format as YYYY-MM-DD and time format as HH:MM.\n"
        + "Appointments can be scheduled in the future only.\n"
        + "Given the following input from the user, please extract the appointment parameters below and return them in JSON format.\n"
        + "IF any of the parameters is missing, return a message in the JSON to ask the user to add the missing information.\n"

        + "Example:\n"
        + "User input: remind me for a meeting  at 10:45 pm.\n"
        + "Returned json:\n"
        + "json:\n"
        + "{\n"
        + '"category": un-categorized\n'
        + '"task_name": "meeting",\n'
        + '"date": {current_time},\n'
        + '"start_time": datetime.time(22,45),\n'
        + "}\n\n"

        + "Parameters:\n"
        + f"task name: {reminder_name.lower()}\n"
        + f"date: {date}\n"
        + f"start_time: {time}\n\n"
        + f"category: {category.lower()}\n"
        + "Please return the JSON object with the reminder name, date, and time."
    )

    parsed_output = {}

    try:
        _json = _json[_json.find("{"):_json.rfind("}") + 1]
        parsed_output = json.loads(_json)


        new_json = parsed_output.copy()
        time_obj = datetime.strptime(new_json["start_time"], "%H:%M")
        date_obj = datetime.strptime(new_json['date'], "%Y-%m-%d")
        start_time_obj = datetime.combine(date_obj.date(), time_obj.time())
        time_iso_format = start_time_obj.isoformat()
        new_json["start_time"] = time_iso_format


    except json.JSONDecodeError:
        return {
            "response": "Failed to parse model output as JSON. Consider alternative parsing methods.",
            "data": {}
        }
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return {
            "response": f"An unexpected error occurred: {e}",
            "data": {}
        }

    date = parsed_output.get("date")
    date = datetime.strptime(date, "%Y-%m-%d").date()
    time = parsed_output.get("start_time")
    print(time)  # to be deleted

    if date < current_date:
        return {
            "response": "Appointments cannot be scheduled in the past.",
            "data": {}
        }
    elif date == current_date:
        try:
            time_obj = datetime.strptime(time, "%H:%M")
            if time_obj.time() <= current_time_plus_2_hours.time():
                return {
                    "response": "Appointments cannot be scheduled for a time in the past. Please choose a future time or a later date.",
                    "data": {}
                }
        except ValueError:
            return {
                "response": "Invalid time format. Please use HH:MM.",
                "data": {}
            }

    del new_json["date"]
    parsed_output = {"schedule_task":new_json}

    print("parsed output: ",parsed_output) # to be deleted
    return insert_schedule_task_to_mongodb(parsed_output, user_id=user_id, category=category, insert_anyway=insert_anyway)

    # return {
    #     "response": "Reminder set successfully.",
    #     "data": parsed_output
    # }

def get_set_reminder_tool():
    return StructuredTool(
        name="set_reminder",
        description="Use this tool to save the reminder_name, date, and time of the reminder.",
        func=set_reminder_tool,
        args_schema=SetReminderToolSchema,
    )








class TaskInputSchema(BaseModel):
    task_name: str = Field(description="The user will enter a name of a task")

def Task(task_name: str):
    try:
        model = ChatOpenAI(temperature=0.2, model='gpt-3.5-turbo-0125', streaming=False)
        _json = model.predict(
            "The user will enter just a task name without saying anything related to that he wants to schedule it,\
            or set a reminder or mentions steps so you will ask him whether he\
            wants to add a task in the calendar or set a reminder or he wants to prepare for this task"

            "Example:"
            "User Input: I have an online meeting"
            "So you will answer him telling do you want to add the task in the calendar or set a reminder or prepare for it"
        )

        response_message = "Do you want to add the task in the calendar or set a reminder or prepare for it"
        return {
            "response": response_message,
            "data": {
                "task_name": task_name
            }
        }

    except OpenAIError as e:
        error_message = "My apologies, an error happened processing your request, can you send it again"
        print(f"OpenAI API request failed to connect: {e}")
        return {
            "response": error_message,
            "data": {}
        }

    except urllib.error.URLError as ue:
        error_message = "You're not connected to the internet. To interact with me, make sure you're connected to the internet"
        print(f"Internet connection error: {ue}")
        return {
            "response": error_message,
            "data": {}
        }

    except Exception as e:
        error_message = "Sorry I couldn't understand your request"
        print(f"An unexpected error occurred: {e}")
        return {
            "response": error_message,
            "data": {}
        }

def get_task():
    return StructuredTool(
        name="Task",
        description="Use this tool when the user just enters a task name without steps or (start and end time) or he doesn't mention that he wants to set a reminder for it.",
        func=Task,
        args_schema=TaskInputSchema
    )


class updateSchema(BaseModel):
    task_name: str = Field(description="the main task name that the user mentions explicitly")
    new_task_name: Optional[str] = Field(
        description="The new name of the task that the user wants it to replace the task name")
    category: Optional[str] = Field(None, description="the category of the main task")
    new_category: Optional[str] = Field(description="New Category of the task to replace the past category")
    text: str = Field(description="The text that the user has entered")
    task_details: object = Field(
        description="the dictionary returned from the getGeneral tool or from the getSchedule tool containing the task's details")
    collection_name: str = Field(description="The name of the collection where the task is found in mongodb")
    update_anyway: bool = Field(False,
                                description="Regardless of the existence of an old task scheduled for the same start time, the user may choose to update their task anyway.")
    user_id: str = Field(description="The id of the user asking for the update")
    Next_start_time: Optional[str] = Field(None, min_length=0,
                                           description="New Start time of the task to replace the past start time only if the user inputs it.leave empty if the user didn't input it")
    Next_end_time: Optional[str] = Field(None, min_length=0,
                                         description="New End time of the task to replace the past end time only of the user inputs it.LEAVE EMPTY IF THE USER DIDN'T INPUT IT.")

def update(task_name, collection_name, user_id, category=None, new_category=None, text=None, task_details={},
                  new_task_name=None, update_anyway=False, Next_start_time=None, Next_end_time=None):
    Mongo_URI = "mongodb+srv://Managenda:Graduationproject2024@cluster0.zs4ebry.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

    try:
        client = MongoClient(Mongo_URI)
        client.admin.command('ping')
        db_name = "Managenda"
        MONGODB_COLLECTION = client[db_name][collection_name]
        logger.info("MongoDB connection established.")

    except errors.ConnectionError as e:
        logger.error(f"MongoDB connection error: {e}")
        return {
            "response": "Failed to connect to MongoDB",
            "data": {"error_details": str(e)}
        }

    except errors.PyMongoError as e:
        logger.error(f"MongoDB error: {e}")
        return {
            "response": "MongoDB error occurred",
            "data": {"error_details": str(e)}
        }

    if task_details:
        task_status = task_details.get("task_status")
        if collection_name == "schedule_tasks" and (task_status == "completed" or task_status == "incomplete"):
            return {
                "response": f"This task is marked as {task_status}, so any edits or updates are currently locked.",
                "data": {}
            }

        prompt1 = f"""
            Given a {text} and details of a task stored in a dictionary {task_details},
            Think very well before you do anything. I'm gonna provide you with the chain of thought BUT you WON'T return it in the output. THIS IS JUST FOR YOU.
            your chain of THOUGHT is as follows:

            1-UNDERSTAND the text very well first:
                - Read and comprehend the provided text thoroughly.

            2-Extract changes:
                -Identify all changes mentioned in the text that need to be applied to the {task_details} ONE BY ONE WITHOUT DROPPING ANY OF THEM.

            3-Compare Knowledge:
                -Compare the NEW details which are the NEW KNOWLEDGE from the text with the existing details (OLD KNOWLEDGE) in the {task_details} dictionary.

            4- Update Rules:
                -AVOID updating the category EVEN IF requested.
                -Update ONLY the fields EXPLICITLY mentioned in the text.
                -AVOID updating fields NOT mentioned by the user.
                -For each mentioned detail, REPLACE the old values in {task_details} with the NEW values from the text.
                -Verify "step_status" before updating STEPS. Skip updates for steps where "step_status" is not "pending" or "in_process".                                

            5-Specific Updates:
                -Duration : Convert new durations to "int32". (e.g., 2.3hrs becomes 138, 1.2hrs becomes 72).  
                -Start/End Time: Ensure the format of the start and end times, whether for the task itself or any of its steps, matches the existing format in the {task_details} dictionary.
                -Steps: Update step names and details AS SPECIFIED. Use the step order as (step 1, step 2) or the step name according to what the user MENTIONS.                 
                -Update the step name ONLY IF the user has asked for it.

            6-Format Notes:
                -Follow the format for start/end times as in the existing {task_details} dictionary values.    
                -"pm" indicates night, and "am" indicated morning.

            7-Return Values:
                -Return ONLY TWO elements in a LIST:
                    First Element: The UPDATED dictionary.
                    Second Element: A summary of the UPDATES MADE.       
                - Do NOT include your chain of thought in the return value. 

            8-Filed Restrictions:
                -AVOID updating "task_status" or "step_status".              
                -AVOID adding, or updating ANYTHING NOT MENTIONED in the text.
        """

        try:
            client = OpenAI(api_key=os.getenv("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"))
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": prompt1},
                ]
            )

            result = completion.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return {
                "response": "Failed to process task update",
                "data": {"error_details": str(e)}
            }


        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            try:
                # Fall back to ast.literal_eval() if JSON parsing fails
                result = ast.literal_eval(result)
            except (TypeError, ValueError, SyntaxError) as e:
                logger.error(f"An error occurred while converting to dict: {e}")
                return {
                    "response": "Failed to parse task update result",
                    "data": {"error_details": str(e)}
                }

        try:
            # Ensure result is a list and first element is a dict
            if not isinstance(result, list) or not isinstance(result[0], dict):
                raise ValueError("Unexpected result format")

            result[0] = dict(result[0])


            # Informing the user that he can't update the category of a task
            category_msg = ""
            if result[0].get("category") != task_details.get("category") or new_category:
                category_msg = "I’ve observed that you wish to modify the category of a specific task. Unfortunately, changing the category for an individual task isn’t possible. You have two options: either manually update the entire category name or create a new task with the desired category."
                result[0]["category"] = task_details["category"]

            result[0]["category"] = task_details["category"]



            new_task_name = result[0]["task_name"]
            category = result[0]["category"]

            if new_task_name != task_details["task_name"]:
                if collection_name == "general_tasks" and MONGODB_COLLECTION.count_documents(
                        {"user_id": user_id, "task_name": new_task_name, "category": category}):
                    return {
                        "response": f"You already have a task named as {new_task_name} in your calendar. Please choose another name to avoid conflicts or keep the name that you've chosen and choose another category.",
                        "data": {}
                    }

            msg = ""
            if collection_name == "schedule_tasks":
                finalized_steps = []
                if "steps" in result[0].keys():
                    for i, step in enumerate(result[0]["steps"]):
                        step_status = step["step_status"]
                        if step_status in ["completed", "incomplete"]:
                            if task_details["steps"][i] != step:
                                result[0]["steps"][i] = task_details["steps"][i]
                                finalized_steps.append(i + 1)
                    if finalized_steps:
                        msg = f"The status of step(s) {', '.join(map(str, finalized_steps))} are finalized, edits are locked on them."

            #To check whether there's a change in the task details or not
            updated = result[0] != task_details

            id = result[0].pop("_id") if isinstance(result[0].get("_id"), str) else result[0].pop("_id")["$oid"]

            if result[0]["task_name"] != task_details["task_name"]:
                result[0]["task_embeddings"] = SelfQuery.generate_embedding(result[0]["task_name"])


            if collection_name == "general_tasks":
                update_res = update_general_task(id, result[0])

            else:
                try:
                    #making sure that the start time of the task is either earlier or equal to the start time of step 1
                    if "steps" in result[0].keys() and len(result[0]["steps"]) > 0:
                        if result[0]["start_time"] > result[0]["steps"][0]["start_time"]:
                            result[0]["start_time"] = result[0]["steps"][0]["start_time"]
                        #making sure that the end time of the task is either later or equal to the end time of the last step
                        if result[0]["end_time"] < result[0]["steps"][-1]["end_time"]:
                            result[0]["end_time"] = result[0]["steps"][-1]["end_time"]

                except TypeError as e:
                    logger.error(f"Type error during time comparison: {e}")
                    return {
                        "response" : "Failed to process task times due to error.",
                        "data" : {}
                    }

                if result[0]["start_time"] == task_details["start_time"] and result[0]["end_time"] == task_details["end_time"]:
                    del result[0]["start_time"]
                    del result[0]["end_time"]

                update_res = update_scheduled_task(id,result[0],update_anyway=update_anyway)


                if (update_res == 'Task conflicts with existing tasks. Do you want to change the time?' or update_res == 'You currently have another task scheduled for the same time. Would you prefer to update the existing task anyway or choose a different time for this task?') and (Next_start_time or Next_end_time):
                    return {
                        "response": "You currently have another task scheduled for the same time. Would you prefer to update the existing task anyway or choose a different time for this task?",
                        "data": {}
                    }


            if "task_embeddings" in result[0].keys():
                del result[0]["task_embeddings"]


            if isinstance(update_res, str):
                return_msg = update_res
                data = result[0]

                if category_msg and updated:
                    return_msg += ". But " + category_msg
                elif category_msg:
                    return_msg = category_msg
                elif not category_msg and not updated:
                    return_msg = "Nothing has been updated."
                if msg:
                    return_msg += " " + msg

            else:
                return_msg = update_res.detail
                data = {}

            return {
                "response": return_msg,
                "data": data
            }

        except (TypeError, ValueError) as e:
            logger.error(f"An error occurred while processing task data: {e}")
            return {
                "response": "An error occurred while processing task data",
                "data": {}
            }

    else:
        return {
            "response": "Oops!! Your task was not found, Make sure of the name of the task you've mentioned",
            "data": {}
        }

def get_update():
    return StructuredTool(
        name="update",
        description="Use this tool when the user wants to update the details of a previously mentioned steps and durations of a general task,besides/"
                    "the parameters that the agent will extract,you're going to use the dictionary returned by the get tool. you are going to USE this tool if the user wants to update"
                    "a task and you DO NOT REMEMBER the task he's talking about in other words it IS NOT in your memory",
        func=update,
        args_schema=updateSchema,
        # return_direct=True
    )



class GetSchema(BaseModel):
    task_name: str = Field(description="the name of the Main task")
    new_task_name: Optional[str] = Field(
        description="The new name of the task that the user wants it to replace the task name, ONLY if the user INPUTS it")
    category: Optional[str] = Field(None, description="The category of the main task, ONLY if the user INPUTS it")
    text: str = Field(description="The text that the user has entered")
    new_category: Optional[str] = Field(description="New Category of the task to replace the past category")
    user_id: str = Field(min_length=1,
         description="The ID of the user. This field is always required, DON'T ever generate a user_id by yourself. Always take this argument from agent's arguments."
    )
def getGeneral(task_name, user_id, category=None, text=None, new_task_name=None, new_category=None):
    Mongo_URI = "mongodb+srv://Managenda:Graduationproject2024@cluster0.zs4ebry.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

    try:
        client = MongoClient(Mongo_URI)
        client.admin.command('ping')
        db_name = "Managenda"
        collection_name = "general_tasks"
        MONGODB_COLLECTION = client[db_name][collection_name]

        myQuery = {"user_id": user_id, "task_name": task_name.lower()}

        if category:
            myQuery["category"] = category.lower()

        try:
            x = MONGODB_COLLECTION.find_one(myQuery, {"task_embeddings": 0, "step_embeddings": 0})

            if x:
                if MONGODB_COLLECTION.count_documents(myQuery) > 1:
                    return {
                        "response": "Oh! It seems that you have several tasks in your calendar with the same name. Could you please provide the category of your task to avoid conflicts",
                        "data": {}
                    }
                else:
                    if new_task_name:
                        category = category or x["category"]
                        if MONGODB_COLLECTION.count_documents(
                                {"user_id": user_id, "task_name": new_task_name, "category": category}) > 0:
                            return {
                                "response": f"You already have a task named as {new_task_name} in your calendar. Please choose another name to avoid conflicts.",
                                "data": {}
                            }
                        else:
                            return {
                                "response": "Task found",
                                "data": {
                                    "task_details": x,
                                    "collection_name": collection_name,
                                    "user_id": user_id
                                }
                            }

                    else:
                        return {
                            "response": "Task found",
                            "data": {
                                "task_details": x,
                                "collection_name": collection_name,
                                "user_id": user_id
                            }
                        }

            else:
                if not category:
                    return {
                        "response": f"It seems there is no task named {task_name} in the database. Could you please check your calendar for the correct task name?",
                        "data": {}
                    }
                else:
                    return {
                        "response": "There's no task with the details that you've provided. Please make sure of the task's details from your calendar.",
                        "data": {}
                    }

        except errors.PyMongoError as e:
            logger.error(f"MongoDB query error: {e}")
            return {
                "response": "An error occurred while querying the database. Please try again later.",
                "data": {"error_details": str(e)}
            }

    except errors.ConnectionError as e:
        logger.error(f"MongoDB connection error: {e}")
        return {
            "response": "An error occurred while connecting to the database. Please try again later.",
            "data": {"error_details": str(e)}
        }

    except errors.PyMongoError as e:
        logger.error(f"MongoDB error: {e}")
        return {
            "response": "A database error occurred. Please try again later.",
            "data": {"error_details": str(e)}
        }

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return {
            "response": "An unexpected error occurred. Please try again later.",
            "data": {"error_details": str(e)}
        }

def get_GetTool():
    return StructuredTool(
        name="getGeneral",
        description="Use this tool before the update tool to fetch the task from the database. Send the output to the update tool BUT keep in mind that \
        you MAY need to re-invoke this method again before sending the output to the update tool.",
        func=getGeneral,
        args_schema=GetSchema,
    )


class getScheduleSchema(BaseModel):
    task_name: str = Field(..., min_length=0,
                           description="name of the task itself mentioned explicitly according to what the user writes")
    new_task_name: str = Field(None, min_length=0,
                               description="new name of the task that the user wants it to replace the old task_name")
    prev_date: Optional[str] = Field(None, min_length=1,
                                     description="Past date of the task only if the user inputs it. ONLY if the user inputs it")
    prev_end_date: str = Field(None, min_length=1, description="PAST DATE of the END time of the task as the user may start a task on a day and finished it on another day\
     SO this parameter will be the date of the end time of the task, ONLY if the user inputs it.")
    prev_start_time: Optional[str] = Field(None, min_length=0,
                                           description="Previous Start time of the task. ONLY if the user inputs it leave it empty if the user didn't input it")
    prev_end_time: Optional[str] = Field(None, min_length=0,
                                         description="Previous End time of the task. ONLY if the user inputs it, leave it EMPTY IF the user DIDN'T input it.")
    prev_category: Optional[str] = Field(None, min_length=0,
                                         description="Past Category of the task that the user has mentioned before. ONLY if the user inputs it")
    Next_category: Optional[str] = Field(None, min_length=0,
                                         description="New Category of the task to replace the past category. ONLY if the user inputs it")
    Next_date: Optional[str] = Field(None, min_length=1,
                                     description="New date of the task to replace the past date,ONLY if the user inputs it")
    Next_start_time: Optional[str] = Field(None, min_length=0,
                                           description="New Start time of the task to replace the past start time only if the user inputs it.leave empty if the user didn't input it")
    Next_end_time: Optional[str] = Field(None, min_length=0,
                                         description="New End time of the task to replace the past end time only of the user inputs it.LEAVE EMPTY IF THE USER DIDN'T INPUT IT.")
    text: str = Field(
        description="The text that the user has entered")
    user_id: str = Field(min_length=1,
         description="The ID of the user. This field is always required, DON'T ever generate a user_id by yourself. Always take this argument from agent's arguments."
    )
    # next_end_date


def getSchedule(task_name, user_id, prev_category=None, text=None, new_task_name=None, Next_category=None,
                prev_end_time=None, prev_start_time=None, prev_date=None, prev_end_date=None, Next_date=None,
                Next_start_time=None, Next_end_time=None):
    if not task_name:
        return {
            "response": "What is the name of the task you want to update?",
            "data": {}
        }

    current_datetime = datetime.now()
    current_date = current_datetime.date()
    current_time = current_datetime.time()
    current_time_plus_2_hours = current_datetime + timedelta(hours=2)
    current_day = current_datetime.strftime('%A')

    try:
        model = ChatOpenAI(temperature=0.2, model='gpt-3.5-turbo-0125')
        _json = model.predict(
            "Given the following input from the user, please extract the appointment parameters below.\n"
            + f"Assume today's date is {current_date} and current time is {current_time_plus_2_hours} and today's day is {current_day}.\n"
        )
    except Exception as e:
        return {
            "response": "Sorry! Could you send your request again",
            "data": {"error_details": str(e)}
        }

    Mongo_URI = "mongodb+srv://Managenda:Graduationproject2024@cluster0.zs4ebry.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

    try:
        client = MongoClient(Mongo_URI)
        client.admin.command('ping')
        db_name = "Managenda"
        collection_name = "schedule_tasks"
        MONGODB_COLLECTION = client[db_name][collection_name]

        task_name = task_name.lower()
        myQuery = {"user_id": user_id, "task_name": task_name}

        if prev_start_time:
            try:
                if prev_date:
                    start_time_obj = datetime.strptime(prev_start_time, "%H:%M").replace(tzinfo=timezone.utc)
                    start_date_obj = datetime.strptime(prev_date, "%Y-%m-%d")
                    start_time_obj = datetime.combine(start_date_obj.date(), start_time_obj.timetz())
                    start_time_obj = start_time_obj.replace(microsecond=0)

                    start_time_obj = start_time_obj.isoformat(timespec='milliseconds')
                    myQuery["start_time"] = datetime.strptime(start_time_obj, "%Y-%m-%dT%H:%M:%S.%f%z")

                else:
                    return {
                        "response": "What's the date of that task?",
                        "data": {}
                    }

            except ValueError as e:
                return {
                    "response": f"Error parsing start time or date: {e}",
                    "data": {}
                }


        if prev_end_time:
            if prev_date and not prev_end_date:
                try:
                    end_time_obj = datetime.strptime(prev_end_time, "%H:%M").replace(tzinfo=timezone.utc)
                    start_date_obj = datetime.strptime(prev_date, "%Y-%m-%d")
                    end_time_obj = datetime.combine(start_date_obj.date(), end_time_obj.timetz())
                    end_time_obj = end_time_obj.replace(microsecond=0)

                    end_time_obj = end_time_obj.isoformat(timespec='milliseconds')
                    myQuery["end_time"] = datetime.strptime(end_time_obj, "%Y-%m-%dT%H:%M:%S.%f%z")
                except ValueError as e:
                    return {
                        "response": f"Error parsing end time or date: {e}",
                        "data": {}
                    }
            elif prev_end_date:
                try:
                    end_time_obj = datetime.strptime(prev_end_time, "%H:%M").replace(tzinfo=timezone.utc)
                    start_date_obj = datetime.strptime(prev_end_date, "%Y-%m-%d")
                    end_time_obj = datetime.combine(start_date_obj.date(), end_time_obj.timetz())
                    end_time_obj = end_time_obj.replace(microsecond=0)

                    end_time_obj = end_time_obj.isoformat(timespec='milliseconds')
                    myQuery["end_time"] = datetime.strptime(end_time_obj, "%Y-%m-%dT%H:%M:%S.%f%z")

                except ValueError as e:
                    return {
                        "response": f"Error parsing end time or end date: {e}",
                        "data": {}
                    }
            else:
                return {
                    "response": "What's the date of that task?",
                    "data": {}
                }

        if prev_date and not prev_start_time and not prev_end_time:
            date_obj = datetime.strptime(prev_date, "%Y-%m-%d").date()
            next_day = date_obj + timedelta(days=1)
            myQuery["start_time"] = {
                "$gte": datetime.combine(date_obj, datetime.min.time()).replace(tzinfo=timezone.utc),
                "$lt": datetime.combine(next_day, datetime.min.time()).replace(tzinfo=timezone.utc)
            }

        if prev_category:
            myQuery["category"] = prev_category.lower()

        print("myQuery: ",myQuery) # to be deleted

        try:
            if MONGODB_COLLECTION.count_documents(myQuery) > 1 and len(myQuery.keys()) < 5:
                return {
                    "response": "Oh! It seems that you have several tasks in your calendar with common details, could you provide more details about your task to avoid conflicts",
                    "data": {}
                }
            elif MONGODB_COLLECTION.count_documents(myQuery) == 0:
                return {
                    "response": f"It seems there is no task named {task_name} in the database. Could you please check your calendar for the correct task name?",
                    "data": {}
                }
            else:
                x = MONGODB_COLLECTION.find_one(myQuery, {"task_embeddings": 0})
                return {
                    "response": "Task found",
                    "data": {
                        "task_details": x,
                        "collection_name": collection_name,
                        "Next_start_time": Next_start_time,
                        "Next_end_time": Next_end_time
                    }
                }

        except errors.PyMongoError as e:
            logger.error(f"MongoDB query error: {e}")
            return {
                "response": "An error occurred while querying the database. Please try again later.",
                "data": {"error_details": str(e)}
            }

    except errors.ConnectionError as e:
        logger.error(f"MongoDB connection error: {e}")
        return {
            "response": "An error occurred while connecting to the database. Please try again later.",
            "data": {"error_details": str(e)}
        }

    except errors.PyMongoError as e:
        logger.error(f"MongoDB error: {e}")
        return {
            "response": "A database error occurred. Please try again later.",
            "data": {"error_details": str(e)}
        }

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return {
            "response": "An unexpected error occurred. Please try again later.",
            "data": {"error_details": str(e)}
        }


def get_GetScheduleTool():
    return StructuredTool(
        name="getSchedule",
        description="Use this tool before the update tool to fetch the task from the database.Send the output to the update tool BUT keep in mind that \
        you MAY  need to re-invoke this method again before sending the output to  the update tool. DO NOT FORGET to extract ALL of the parameters \
                    ONLY if the user inputs them  ",
        func=getSchedule,
        args_schema=getScheduleSchema,
    )


class initiateGeneralSchema(BaseModel):
    task_name: str = Field(min_length=1, description="The name of the task that the user has entered")
    start_time: str = Field(None, description="The time at which the user wants to begin the general task. PAY ATTENTION! am or pm may be appended to the start_time\
                                             you SHOULD NOT extract them with the time, ONLY use them to calculate the start_time correctly\
                                             Example: 7:40pm the start_time will be JUST 19:40\
                                             Example: 8:10am the start_time will be JUST 8:10")
    date: str = Field(None,
                      description="The date at which the user wants to initiate his general task. it SHOULD be in this format %Y-%m-%d")
    category: str = Field(None, description="The category of the main task ONLY if the user inputs it")
    insert_anyway: bool = Field(False,
                                description="Regardless of the existence of an old task scheduled for the same start time, the user may choose to insert their task anyway.")
    user_id: str = Field(min_length=1,
         description="The ID of the user. This field is always required, DON'T ever generate a user_id by yourself. Always take this argument from agent's arguments."
    )


def initiateGeneral(task_name, user_id, start_time=None, category=None, date=None, insert_anyway=False):
    current_datetime = datetime.now()
    current_date = current_datetime.date()
    current_time = current_datetime.time()
    current_time_plus_2_hours = current_datetime + timedelta(hours=2)
    current_day = current_datetime.strftime('%A')

    if not start_time:
        return {
            "response": f"When do you want to start the general task named as {task_name} in your calendar?",
            "data": {}
        }

    if not date:
        return {
            "response": f"What date works best for you to initiate the task {task_name}?",
            "data": {}
        }

    date_obj = datetime.strptime(date, "%Y-%m-%d").date()

    if date_obj < current_date:
        return {
            "response": "Tasks cannot be initiated in the past. Please choose a date in the future",
            "data": {}
        }

    elif date_obj == current_date:
        if start_time:
            try:
                start_time_obj = datetime.strptime(start_time, "%H:%M")
                if start_time_obj.time() <= current_time_plus_2_hours.time():
                    return {
                        "response": "Tasks cannot be initiated for a time in the past. Please choose a future time or a later date.",
                        "data": {}
                    }
            except ValueError:
                return {
                    "response": "Invalid time format. Please use HH:MM.",
                    "data": {}
                }

    if start_time and date:
        Mongo_URI = "mongodb+srv://Managenda:Graduationproject2024@cluster0.zs4ebry.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

        try:
            client = MongoClient(Mongo_URI)
            client.admin.command('ping')

            db_name = "Managenda"
            collection_name = "general_tasks"
            MONGODB_COLLECTION = client[db_name][collection_name]

            myQuery = {"user_id": user_id, "task_name": task_name.lower()}

            if category:
                myQuery["category"] = category

            x = MONGODB_COLLECTION.find_one(myQuery, {"task_embeddings": 0})

            if x:
                if MONGODB_COLLECTION.count_documents(myQuery) > 1 and not category:
                    return {
                        "response": f"Oh! It seems that you have several tasks in your calendar with the same name, could you provide the category of this task to avoid conflicts",
                        "data": {}
                    }
                else:
                    try:
                        datetime_str = f"{date} {start_time}"
                        dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
                        start_iso_format = dt.isoformat(timespec='milliseconds') + 'Z'
                        x["start_time"] = start_iso_format

                        flag = True
                        end_time = None

                        if "steps" in x.keys():
                            for i, step in enumerate(x["steps"]):
                                if "duration" in step:
                                    if step["duration"] != 0:
                                        if i == 0:
                                            step["start_time"] = start_iso_format
                                        elif flag:
                                            step["start_time"] = x["steps"][i - 1]["end_time"]
                                        else:
                                            prev_start_time = datetime.fromisoformat(x["steps"][i - 1]["start_time"].replace('Z', '+00:00'))
                                            prev_start_time = prev_start_time + timedelta(minutes=1)
                                            step["start_time"] = prev_start_time.isoformat()

                                        iso_start_datetime = datetime.fromisoformat(step["start_time"].replace('Z', '+00:00'))
                                        step["end_time"] = (iso_start_datetime + timedelta(minutes=step["duration"])).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
                                        end_time = step["end_time"]
                                    else:
                                        flag = False
                                        if i == 0:
                                            step["start_time"] = start_iso_format
                                        else:
                                            step["start_time"] = x["steps"][i - 1]["end_time"]

                            step_fields = ["step_status", "duration"]
                            steps = x.get("steps", [])
                            for step in steps:
                                for field in list(step.keys()):
                                    if field in step_fields:
                                        del step[field]
                        if not category:
                            category = x["category"]

                        x = {k: x[k] for k in ["task_name", "steps", "start_time"]}
                        x["end_time"] = end_time
                        x = {"schedule_task": x}

                        return insert_schedule_task_to_mongodb(x,user_id=user_id, category=category, insert_anyway=insert_anyway)


                    except ValueError as e:
                        return {
                            "response": f"Error parsing date or time: {e}",
                            "data": {}
                        }
                    except KeyError as e:
                        return {
                            "response": f"Missing expected key: {e}",
                            "data": {}
                        }
                    except Exception as e:
                        return {
                            "response": "An unexpected error occurred while processing the task.",
                            "data": {"error_details": str(e)}
                        }

            else:
                if not category:
                    most_similar_task = SelfQuery.get_similar_task(task_name.lower(), user_id, "vector_index", collection_name, "task_embeddings")
                    if most_similar_task:
                        return {
                            "response": f"There's no task named as such in your calendar. Do you mean the task named as {most_similar_task}?",
                            "data": {}
                        }
                    else:
                        return {
                            "response": "There's no task named as such in your calendar. Please check the name of your task from your calendar.",
                            "data": {}
                        }
                else:
                    return {
                        "response": f"It seems there is no task named {task_name} in the database. Could you please check your calendar for the correct task name?",
                        "data": {}
                    }

        except errors.ConnectionError as e:
            return {
                "response": "An error occurred while connecting to the database. Please try again later.",
                "data": {"error_details": str(e)}
            }
        except errors.PyMongoError as e:
            return {
                "response": "A database error occurred. Please try again later.",
                "data": {"error_details": str(e)}
            }
        except Exception as e:
            return {
                "response": "An unexpected error occurred. Please try again later.",
                "data": {"error_details": str(e)}
            }


def get_initiateGeneral():
    return StructuredTool(
        name="initiateGeneral",
        description="Use this tool when the user wants to start a previously entered task",
        func=initiateGeneral,
        args_schema=initiateGeneralSchema,
        # return_direct = True
    )



#DELETE
class ProposeDeleteTaskSchema(BaseModel):
    task_name: str = Field(..., description="The name of the task to be potentially deleted")
    user_id: str = Field(..., description="The identifier of the user who owns the task")
    collection_name: str = Field(..., description="The name of the collection where the task is stored")


def propose_delete_task(task_name: str, user_id: str, collection_name: str) -> dict:
    try:
        client = Constants.client
        client.admin.command('ping')
        db = client.get_database("Managenda")
        SCHEDULE_COLLECTION = db.get_collection("schedule_tasks")
        GENERAL_COLLECTION = db.get_collection("general_tasks")

        query = {"task_name": task_name, "user_id": user_id}
        schedule_task = SCHEDULE_COLLECTION.find_one(query)
        general_task = GENERAL_COLLECTION.find_one(query)

        if schedule_task and general_task:
            return {
                "response": "Are you sure that you want to delete the task from schedule or general tasks?",
                "data": {
                    "task_name": task_name,
                    "collection_name": collection_name,
                    "is_similar": False,
                    "options": [
                        {"task_name": schedule_task["task_name"], "collection_name": "schedule_tasks"},
                        {"task_name": general_task["task_name"], "collection_name": "general_tasks"}
                    ]
                }
            }

        if schedule_task:
            return {
                "response": "Task found in schedule collection. Confirm to proceed with deletion. This action cannot be undone.",
                "data": {
                    "task_name": task_name,
                    "collection_name": "schedule_tasks",
                    "is_similar": False
                }
            }

        if general_task:
            return {
                "response": "Task found in general collection. Confirm to proceed with deletion. This action cannot be undone.",
                "data": {
                    "task_name": task_name,
                    "collection_name": "general_tasks",
                    "is_similar": False
                }
            }

        most_similar_task, collection = SelfQuery.retrieve_most_similar_task_from_the_both_collections(task_name, user_id)
        if most_similar_task:
            return {
                "response": f"Exact task not found. Found similar task '{most_similar_task}'. Confirm to delete this task instead. This action cannot be undone.",
                "data": {
                    "task_name": most_similar_task,
                    "collection_name": collection,
                    "is_similar": True
                }
            }

        return {
            "response": "No task or similar task found.",
            "data": {}
        }

    except errors.ConfigurationError as e:
        return {
            "response": f"MongoDB connection error: {e}",
            "data": {}
        }
    except errors.PyMongoError as e:
        return {
            "response": f"MongoDB error: {e}",
            "data": {}
        }
    except Exception as e:
        return {
            "response": f"An error occurred: {e}",
            "data": {}
        }

def get_propose_delete_task():
    return StructuredTool(
        name="propose_delete_task",
        description="Use this tool to propose the deletion of a task and ask for confirmation. This action is permanent.",
        func=propose_delete_task,
        args_schema=ProposeDeleteTaskSchema,
    )





def confirm_and_delete_task(task_name: str, user_id: str, collection_name: str) -> dict:
    try:
        client = Constants.client
        client.admin.command('ping')
        db = client.get_database("Managenda")
        collection = db.get_collection(collection_name)

        query = {"task_name": task_name, "user_id": user_id}
        result = collection.delete_one(query)

        if result.deleted_count > 0:
            return {
                "response": "Task deleted successfully.",
                "data": {
                    "task_name": task_name,
                    "user_id": user_id,
                    "collection_name": collection_name
                }
            }
        else:
            return {
                "response": "Task deletion failed. It may have already been deleted or not found.",
                "data": {
                    "task_name": task_name,
                    "user_id": user_id,
                    "collection_name": collection_name
                }
            }

    except errors.ConfigurationError as e:
        return {
            "response": f"MongoDB connection error: {e}",
            "data": {}
        }
    except errors.PyMongoError as e:
        return {
            "response": f"MongoDB error: {e}",
            "data": {}
        }
    except Exception as e:
        return {
            "response": f"An error occurred during the deletion process: {e}",
            "data": {}
        }


def get_confirm_and_delete_task():
    return StructuredTool(
        name= "delete_task",
        description= """You should use this tool after user's deletion confirmation or after invoking propose_delete_task tool, After ensuring the confirmation of task deletion, This tool allows users to directly delete tasks from the MongoDB database. It's designed for removing tasks that are no longer needed, such as completed tasks not to be repeated or tasks added by mistake. The deletion targets a specific task based on its name, and the owning user's ID, ensuring precision in the operation. Users are advised to carefully confirm task details before deletion due to the irreversible nature of this action. Use with caution to avoid unintended data loss. """,
        func= confirm_and_delete_task,
        args_schema= ProposeDeleteTaskSchema,
    )





#GET
class RetrieveTaskSchema(BaseModel):
    user_id: str = Field(..., description="The identifier of the user who owns the task")
    task_name: str = Field(..., description="The name of the task to be retrieved")


def retrieve_task(user_id: str, task_name: str) -> dict:
    query = {"task_name": task_name, "user_id": user_id}
    try:
        client = Constants.client
        client.admin.command('ping')
        db = client.get_database("Managenda")

        SCHEDULE_COLLECTION = db.get_collection("schedule_tasks")
        GENERAL_COLLECTION = db.get_collection("general_tasks")

        schedule_task = SCHEDULE_COLLECTION.find_one(query)
        general_task = GENERAL_COLLECTION.find_one(query)

        logger.info("MongoDB connection established.")
    except errors.ConfigurationError as e:
        logger.error(f"MongoDB connection error: {e}")
        return {
            "response": f"MongoDB connection error: {e}",
            "data": {}
        }
    except errors.PyMongoError as e:
        logger.error(f"MongoDB error: {e}")
        return {
            "response": f"MongoDB error: {e}",
            "data": {}
        }

    try:
        if schedule_task:
            logger.info("Schedule task found")
            return {
                "response": "Task found in schedule collection.",
                "data": schedule_task
            }

        if general_task:
            logger.info("General task found")
            return {
                "response": "Task found in general collection.",
                "data": general_task
            }

        logger.info("Finding similar tasks")

        most_similar_task, collection = SelfQuery.retrieve_most_similar_task_from_the_both_collections(task_name, user_id)

        if most_similar_task:
            return {
                "response": f"There's no task named '{task_name}' in your calendar. Did you mean the task named '{most_similar_task}'?",
                "data": {}
            }

        return {
            "response": f"There's no task named '{task_name}' in your calendar. Please check the name of your task from your calendar.",
            "data": {}
        }

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return {
            "response": f"An error occurred while retrieving the task: {e}",
            "data": {}
        }

def get_retrieve_task_tool():
    return StructuredTool(
        name="retrieve_task",
        description="Retrieves all information about a specific task using the task's name and the user's unique identifier. If the task is not found, it suggests similar task names for that user.",
        func=retrieve_task,
        args_schema=RetrieveTaskSchema,
    )














class TimeManagementToolSchema(BaseModel):
    query: str = Field(..., min_length=1, description="User questions about time management and procrastination")


def process(query):
    results = Constants.PINECONE_DOSEARCH.similarity_search(query, k=5)
    context = ",".join(str(x) for x in results)
    messages = [
        {"role": "system",
         "content": "As an assistant, your role is to provide help based strictly on the information contained in "
                    "the documents provided. Your responses should be derived solely from these documents. "
                    "It’s important that you do not generate answers based on any external knowledge or "
                    "information not present in the documents. You could get results from multiple PDFs. "
                    "State only the most appropriate answer provided from the contexts in a bullet form with format '{{answer that you generate}}'. "
                    "If the question isn't related to the context, don't answer and respond with 'Sorry, but this question isn't in your PDFs'."}
    ]
    if not results:
        messages.append({"role": "system", "content": "Sorry, no context found for this question."})
    messages.append({"role": "user", "content": context})
    messages.append({"role": "user", "content": query})
    response = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
    answer = response.choices[0].message.content.replace('\n', ' ')
    return {
        "response": answer,
        "data": {}
    }

def get_time_management_tool():
    return StructuredTool(
        name="time_management",
        description="Use this tool to answer user questions about time management and procrastination.",
        func=process,
        args_schema=TimeManagementToolSchema,
    )
