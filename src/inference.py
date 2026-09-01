import chainlit as cl 
from chainlit.user import User
import uuid
from models import Message,IntentHistory
from rich.pretty import pprint
from langgraph.types import Command
from plotfunc import Get_Plots
from graph import Agent
from utils import get_current_history

from logger import logger
from dotenv import load_dotenv

load_dotenv()

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


async def handle_interruption(result, config):
    """
    Handles an intent clarification interrupt raised by LangGraph.
    """

    if "__interrupt__" not in result:
        return result

    interrupt_data = result["__interrupt__"][0].value

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
        return None

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
                cl.input_widget.Slider(
                    id="Max_retries",
                    label="Max retries ",
                    initial_index=2,
                    min=2,
                    max=5,
                    step=1
                ),
                cl.input_widget.Switch(
                    id="plots",
                    label="Generate visualizations",
                    initial=True,
                ),
            ]
        ).send()

    cl.user_session.set(
        "Max_retries",
        settings["Max_retries"]
    )
    cl.user_session.set(
        "plots",
        settings["plots"]
    )


@cl.on_settings_update
async def setup_agent(settings):
    cl.user_session.set(
        "Max_retries",
        settings["Max_retries"]
    )

    cl.user_session.set(
        "plots",
        settings["plots"]
    )


@cl.on_message
async def main(message: cl.Message):

    thread_id = cl.user_session.get("thread_id")
    Max_retries = cl.user_session.get("Max_retries")
    plots_enabled = cl.user_session.get("plots")
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
    "Max_retries":Max_retries,
    "plots_enabled":plots_enabled,
    "data_context": "",
    "intent_histories": [
        new_intent_history
    ],
    }

    logger.info(f"number of retries is {Max_retries}")
    result = await Agent.ainvoke(
        initial_state,
        config=config
    )

    
    # if the agent needs clarification 
    if "__interrupt__" in result:
        result = await handle_interruption(
            result,
            config
        )
        result  = await handle_interruption(result,config)

    if result is None:
        return
    
    response = result["response"]

    # generate the plot if enabled
    figures = []
    allplots = result.get("allplots")

    if (
        plots_enabled
        and response.visualization 
        and  allplots
        ) :

        figures = Get_Plots(result)

    msg = await cl.Message(
        content=response.answer
    ).send()

    for fig in figures:
        await cl.Plotly(
            name=fig.layout.title.text,
            figure=fig,
            display="inline"
        ).send(for_id=msg.id) 





