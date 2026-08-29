import chainlit as cl 
from chainlit.user import User
import uuid
from graph import Agent 
from models import Message,IntentHistory



@cl.on_chat_start
async def start():

    thread_id = str(uuid.uuid4())
    cl.user_session.set(
        "thread_id",
        thread_id
    )

    await cl.Message(
        content="Hello! How can I help you?"
    ).send()

@cl.on_message
async def main(message: cl.Message):

    thread_id = cl.user_session.get("thread_id")
    message_id = str(uuid.uuid4())

    new_message = Message(
        id=message_id,
        HumanMessages=message.content,
        AIMessages=""
    )

    new_intent_history=IntentHistory(
        message_id=message_id,
        intents=[]
    )

    initial_state = {
    "messages": [new_message],
    "data_context": "",
    "intent_histories": [
        new_intent_history
    ],
    }

    config = {
        "configurable":{"thread_id":thread_id}
    }

    result = await Agent.ainvoke(
        initial_state,
        config=config
    )
    response = result['response']
    await cl.Message(
        content=response.answer
    ).send()
    