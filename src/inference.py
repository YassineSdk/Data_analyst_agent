import chainlit as cl 
from chainlit.user import User
import uuid
from graph import Agent 
from models import Message,IntentHistory


@cl.set_starters
async def set_starters():
    return[
        cl.Starter(
            label="Sales Summary",
            message="""Give me a sales performance summary for 2025,
                including total revenue, total COGS, total profit, and total quantity sold.
                Compare the results with 2024 and highlight the main changes.
            """,
            icon="/public/sales.svg"
        ),
        cl.Starter(
            label="Product Performance",
            message="""
            Analyze product performance for 2025. Show me the top 5 products by total revenue,
            their total quantity sold and profit, and identify which products performed the best overall.
            """,
            icon="/public/products_perf.svg"
        ),
        cl.Starter(
            label="Regional Performance",
            message="""
            Analyze sales performance by region for 2025. Show total revenue,
            total COGS, total profit, and quantity sold for each region,
            then identify the strongest and weakest performing regions.
            """,
            icon="/public/regional_perf.svg"
        )
    ]


@cl.on_chat_start
async def start():

    thread_id = str(uuid.uuid4())
    cl.user_session.set(
        "thread_id",
        thread_id
    )

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
    
