from openai import OpenAI
from openai_assistant.config import cfg

openai_api_key = cfg["OPENAI_API_KEY"]
client: OpenAI = OpenAI(api_key=openai_api_key)

def get_oai_client():
    return client

def get_assistant(id):
    return client.beta.assistants.retrieve(id)

def list_messages(thread_id):
    messages = client.beta.threads.messages.list(thread_id, limit=100, order="asc")
    list = []
    for msg in messages:
        list.append(msg.content[0].text.value)
    return list

def create_assistant(name, model, instructions, tools, file_ids):
    asst = client.beta.assistants.create(name=name, model=model, instructions=instructions,  # ,
        tools=tools, file_ids=file_ids)
    return asst

def create_thread():
    return client.beta.threads.create()

def create_message(thread_id, role, msg):
    return client.beta.threads.messages.create(thread_id=thread_id, role=role, content=msg)

def create_run(thread_id, assistant_id):
    return client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)

def get_run(thread_id, run_id):
    return client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)

def get_thread_messages(thread_id):
    return client.beta.threads.messages.list(thread_id=thread_id)

def submit_tool_outputs(thread_id, run_id, tool_outputs):
    return client.beta.threads.runs.submit_tool_outputs(thread_id=thread_id, run_id=run_id, tool_outputs=tool_outputs)
