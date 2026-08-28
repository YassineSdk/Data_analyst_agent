import chainlit as cl 
from chainlit.user import User
import uuid
from graph import Agent 



@cl.on_chat_start
async def start():
    thread_id = str(uuid.uuid1())
    
    cl.user_session.set("thread_id",thread_id)


@cl.on_message
async def main(message: cl.Message):
    thread_id = cl.user_session.get("thread_id")

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    
