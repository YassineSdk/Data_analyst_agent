import chainlit as cl 
from chainlit.user import User
import uuid
from models import Message,IntentHistory
from rich.pretty import pprint
from langgraph.types import Command

from graph import Agent



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



async def handle_interruption(result,config):
    """
    """
    if "__interrupt__" not in result:
        return result

    interrupt_data =  result["__interrupt__"][0].value

    if interrupt_data["type"] != "intent_clarification":
        return result
    
    question = interrupt_data["question"]
    response = await cl.AskUserMessage(
        content=question,
        timeout=300
        ).send()

    if not response:
        await cl.Message(
            content="I didn't receive any clarification."
        ).send()

    user_feedback = response["output"]
    resumed_result = await Agent.ainvoke(
    Command(resume=user_feedback),
    config=config
    )

    return resumed_result


@cl.on_chat_start
async def start():

    thread_id = str(uuid.uuid4())
    cl.user_session.set(
        "thread_id",
        thread_id
    )

    settings = await cl.ChatSettings(
            [
                cl.input_widget.Select(
                    id="interaction_mode",
                    label="Interaction Mode",
                    values=[
                        "Automatic",
                        "Ask for clarification"
                    ],
                    initial_index=0,
                ),
            ]
        ).send()

    cl.user_session.set(
        "interaction_mode",
        settings["interaction_mode"]
    )


@cl.on_settings_update
async def setup_agent(settings):
    cl.user_session.set(
        "interaction_mode",
        settings["interaction_mode"]
    )



@cl.on_message
async def main(message: cl.Message):

    thread_id = cl.user_session.get("thread_id")
    mode = cl.user_session.get("interaction_mode")
    message_id = str(uuid.uuid4())
    config = {
        "configurable":{"thread_id":thread_id}
    }

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
    "mode":mode,
    "data_context": "",
    "intent_histories": [
        new_intent_history
    ],
    }

    result = await Agent.ainvoke(
        initial_state,
        config=config
    )

    # if the agent needs clarification 
    result  = await handle_interruption(result,config)

    if result is None:
        return
    
    response = result["response"]

    await cl.Message(
        content=response.answer
    ).send()





