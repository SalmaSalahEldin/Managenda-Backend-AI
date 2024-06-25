from datetime import datetime, timedelta
from langchain_core.prompts import MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.memory import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from Chatbot import Tools
import logging

logger = logging.getLogger(__name__)

tools = [
    Tools.get_general_task_tool(),
    Tools.get_schedule_task_tool(),
    Tools.get_set_reminder_tool(),
    Tools.get_task(),
    Tools.get_update(),
    Tools.get_GetTool(),
    Tools.get_GetScheduleTool(),
    Tools.get_initiateGeneral(),
    Tools.get_propose_delete_task(),
    Tools.get_confirm_and_delete_task(),
    Tools.get_retrieve_task_tool(),
    Tools.get_time_management_tool(),
]
current_datetime = datetime.now()
current_datetime_message = [{"role": "assistant", "content": str(current_datetime)}]

current_date = current_datetime.date()
current_date_message = [{"role": "assistant", "content": str(current_date)}]

current_time = current_datetime.time()
current_time_message = [{"role": "assistant", "content": str(current_time)}]

current_time_plus_2_hours = current_datetime + timedelta(hours=2)
current_time_plus_2_hours_message = [{"role": "assistant", "content": str(current_time_plus_2_hours)}]

current_day = current_datetime.strftime('%A')
current_day_message = [{"role": "assistant", "content": str(current_day)}]

llm_chat = ChatOpenAI(temperature=0.2,model='gpt-4-0125-preview', streaming=False)

# llm_chat = ChatOpenAI(temperature=0.0, model='gpt-3.5-turbo-0125', streaming=False)
# llm_chat = ChatOpenAI(temperature=0.2, model='gpt-4-turbo', streaming=False)
# llm_chat = ChatOpenAI(temperature=0.2, model='gpt-4o', streaming=False)

system_template = ("""
        You are an executive assistant responsible for managing appointment scheduling, task preparation, and maintaining a knowledge base.
        
        Instructions:
        1. You will always receive a {user_id} variable. Use it as an argument for any of your tools. Do not generate a {user_id} yourself; always use the one provided.
        2. Assume today's date is {current_date}, the current time is {current_time_plus_2_hours}, and today's day is {current_day}. You cannot schedule anything in the past.
        3. The user will interact with you in the following ways:
           a. Use the schedule_task tool with category, start_time, end_time, date, and task_name.
              - If a date is not specified, assume {current_date}.
              - Prompt the user for the start time if it is not provided: "What is the start time for the appointment?"
              - Prompt the user for the end time if it is not provided: "What is the end time for the appointment?"
              - Prompt the user for the category if it is not provided: "Would you like to add your task to a category or leave it uncategorized?"
           b. Use the set_reminder tool with time, date, and reminder name.
              - If a date is not specified, assume {current_date}.
           c. If the user provides a sequence of steps for a task, use the general_task tool to extract the main task category, name, steps, and duration for each step.
              - If no duration is mentioned for a step, assign "0 minutes."
              - Recognize and use abbreviations for units of time (e.g., "h," "hr," "hrs" for hours).
              - If the main task category is not specified, leave it as None.
              - If the user's request includes scheduling and steps, use both the schedule_task and general_task tools.
           d. If the user enters just a task name, use the Task tool to ask if they want to add it to the calendar, set a reminder, or prepare for it.
              - Do not suggest steps unless the user requests them.
           e. If the user asks about the duration of a step and it hasn't been mentioned before, inform them you don't have that information.
              - If a duration is mentioned without a unit, ask the user to specify the unit.
        4. Extract all relevant details from the user's message according to the tools you have.
           - If information is missing, ask the user for it.
           - Use your memory to recall previously mentioned tasks, steps, times, and dates.
           - Provide appropriate responses based on the user's questions about past tasks and steps.
           - Update the extracted dictionary if the user updates any task information.
        5. Use the update tool if the user wants to update task details.
           - If the task name is not explicitly mentioned, ask for it.
        6. Use the Access tool if the user asks about tasks on a specific day or date and time.
        7. Always respond in JSON format.
        8. Only answer questions related to time management and procrastination.
        9. Use the time_management_database for questions about time management and procrastination.
        10. Invoke only one tool at a time and do not use multiple tools simultaneously for the same task.
            - If an error occurs with a tool, inform the user: "Sorry, there is an error. You should contact us."
        11. Do not invoke get_confirm_and_delete_task without invoking get_propose_delete_task first.
        12. Ensure to always extract all steps.
        13. If there is a conflict with an existing task, ask the user: "Would you like to insert it anyway?"
        
        Here is the chat history:
        {chat_history}
        
        Here is some more text:
        {input}
        """)

# .format(current_date=current_date, current_time_plus_2_hours=current_time_plus_2_hours, current_day=current_day))

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_template),
        ("user", "{input}"),
        # ("user", "{user_id}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
        MessagesPlaceholder(variable_name="current_date"),
        MessagesPlaceholder(variable_name="current_time_plus_2_hours"),
        MessagesPlaceholder(variable_name="current_day"),
        MessagesPlaceholder(variable_name="user_id"),
        MessagesPlaceholder(variable_name="chat_history"),
        # MessagesPlaceholder(variable_name="human_input"),
    ]
)

memory = ChatMessageHistory(session_id="test-session")

agent = create_openai_tools_agent(llm=llm_chat, tools=tools, prompt=prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    handle_parsing_errors=True,
    return_intermediate_steps=True,
    verbose=True,
)

agent_with_chat_history = RunnableWithMessageHistory(
    agent_executor,
    lambda session_id: memory,
    input_messages_key="input",
    history_messages_key="chat_history",
)

# user_id = 'salma'

# text = "For alda lessoion  for an hour, I start with a warm-up for half an hour, move on to cardio exercises,make sure to hydrate put it in category work"


# txt = "schedule an online meetinganoompomhqeasooo from 10 am to 11 am add it to category work step one is to do a presentation from 5am to 6 am and step two is to listen to music from 6 am to 7 am"

# text = "i confirm that i want to delete english lesson task"

# text = "retrieve information about english lesson task"
# text = "what is time management skills"

# text = "I want to studyfdelijn, listen to a 1h lecture"

# text = "I have a project discsussiaonsann on thursday so schedule it invoke the schedule tool ,it starts 12:30 afternoon and ends at 1:30 afternoon, first step is to prepare a presentation from 5:30 afternoon to 6:30 afternoon, second step is to listen to music from 6 am to 7 am, add it to category work if there is a conflict with any existing task also add this task"
# text = "i want to update the task named physics class in general task collection to be named physics classs"

def send_msg(text, user_id):
    user_id = [{"role": "assistant", "content": user_id}]
    res = agent_with_chat_history.invoke(
        {
            "input": text,
            "user_id": user_id,
            "current_date": current_date_message,
            "current_day": current_day_message,
            "current_time_plus_2_hours": current_time_plus_2_hours_message,
        },
        {
            "configurable": {
                "session_id": "test-session"
            }
        }
    )

    output = None
    data = None
    if 'intermediate_steps' in res:
        for step in res['intermediate_steps']:
            if isinstance(step, tuple) and len(step) == 2:
                step_data = step[1]
                if step_data:
                    response = step_data.get('response')
                    if response:
                        output = response
                    step_data_content = step_data.get('data')
                    if step_data_content:
                        data = step_data_content
                    break

    response = {
        'response': output,
        'data': data
    }

    return response

# print("outputtttttttttttttttttttt")
# print(send_msg(text, user_id))