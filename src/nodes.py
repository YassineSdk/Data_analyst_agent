
from langgraph.types import interrupt
from rich.pretty import pprint

from logger import logger
from state import AgentState
from models import ExecutionState, IntentHistory
from agents import (
    sql_generator_llm,
    sql_auditor_llm,
    result_analyst_llm,
    intent_analyst_llm,
    plot_analyst_llm,
    out_of_domain_llm
)
from excuter import sql_executor
from utils import (intent_template_maker,
        read_context ,
        get_current_history
        )
import pandas as pd 
from models import AnalystResponse
import chainlit as cl


Data_CONTEXT = read_context("data_context.txt")


async def intent_analyst(state: AgentState) -> dict:
    
    current_step = cl.context.current_step
    logger.info("Starting the intent analyst")
    human_template = intent_template_maker(state)

    # Generating the new intent
    result = await intent_analyst_llm.ainvoke(
        {
            "human_template": human_template
        }
    )
    
    # Derive if clarification is still needed 
    if result.needs_clarification:
        current_step.input = "the agent needs clarification"

        # Pause the graph and ask the user
        feedback = interrupt(
                    {
                        "type": "intent_clarification",
                        "question": result.clarification
                    }
                )
        # adding feedback to the result
        result.feedback = feedback
    pprint(result)
    # create new intent 
    new_history = IntentHistory(
    message_id=state["messages"][-1].id,
    intents=[result]
    )

    return {
        "intent_histories": [new_history]
    }



async def sql_generator(state: AgentState)-> dict :
    """
    generates an SQL script that solves the users query
    """

    logger.info("starting the SQL generator agent")

    latest_message = state["messages"][-1]
    history,latest_intent =  get_current_history(state)
    
    human_template =f"""
    User query:
    {latest_message.HumanMessages}

    Data context :
    {Data_CONTEXT}

    intent : 
    {latest_intent.interpretation}
    feedback:
    {latest_intent.feedback or None }
    """

    result = await sql_generator_llm.ainvoke(
        {
        "human_template":human_template
        }
    )
    pprint(result)

    return {
        "sql":result
    }



async def sql_auditor(state:AgentState)->dict:
    """
    Audit the generated SQL query.
    """
    logger.info("starting the SQL auditor agent")

    latest_message = state["messages"][-1]
    history,latest_intent = get_current_history(state)

    human_template = f"""
    User query:
    {state["messages"][-1].HumanMessages}

    Data context:
    {Data_CONTEXT}

    SQL Query:
    {state['sql']}

    Current intent:
    {latest_intent.interpretation}

    Feedback:
    {latest_intent.feedback or "None"}
    """

    result = await sql_auditor_llm.ainvoke({
        "human_template":human_template
    })

    pprint(result)
    return {
        "audit":result
    }



async def result_analyst(state:AgentState)->dict:
    """
    Analyze the execution result and generate the final response.
    """

    logger.info("starting the result analyst agent")

    latest_message = state["messages"][-1]
    history,latest_intent =  get_current_history(state)

    human_template = f"""
    Validated user intent:
    {latest_intent.interpretation}

    Execution result:
    {state["execution"]}
    """

    result = await result_analyst_llm.ainvoke({
        "human_template":human_template
    })
    pprint(result)
    return {
        "response":result
    }



async def execute(state:AgentState)->dict:
    """
    executes the SQL code 
    """

    logger.info("executing the SQL query")

    result =  sql_executor.execute(
        state["sql"].query
    )

    pprint(result)
    return {
        "execution":ExecutionState(**result)
    }



async def plot_builder(state:AgentState)->dict:
    """
    """

    logger.info("starting the plotting agent ")

    _,current_intent = get_current_history(state)

    human_template = f"""
    rows:
    {state["execution"].result}

    rows:
    {state["execution"].columns}

    intent :
    {current_intent.interpretation}
    """

    result = await plot_analyst_llm.ainvoke({
        "human_template":human_template
        }
    )
    pprint(result)

    return {
        "allplots":result
    }



async def out_of_domain(state):
    """
    """
    conversation = "\n".join(
        f"Human:{message.HumanMessages}\n"
        for message in state["messages"]
    )
    human_template = f"""
    Conversation history :
    {conversation}

    data_context :
    {Data_CONTEXT}
    """

    result = await out_of_domain_llm.ainvoke(
        {
            "human_template":human_template
        }
    )
    pprint(result)
    return {
        "redirect": result
    }



