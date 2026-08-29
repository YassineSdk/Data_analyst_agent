
from langgraph.types import interrupt
from rich.pretty import pprint

from logger import logger
from state import AgentState
from models import ExecutionState, IntentHistory
from agents import (
    sql_generator_llm,
    sql_auditor_llm,
    result_analyst_llm,
    intent_analyst_llm
)
from excuter import sql_executor
from utils import intent_template_maker, read_context



Data_CONTEXT = read_context("data_context.txt")

def intent_analyst(state: AgentState) -> dict:
    
    logger.info("Starting the intent analyst")
    human_template = intent_template_maker(state)

    result = intent_analyst_llm.invoke(
        {
            "human_template": human_template
        }
    )

    result.approved = True
    result.feedback = None

    pprint(result)
    message_id = state["messages"][-1].id

    # Find the current history
    history = next(
        h
        for h in state["intent_histories"]
        if h.message_id == message_id
    )

    # Create a NEW history with the new intent
    updated_history = IntentHistory(
        message_id=history.message_id,
        intents=[
            *history.intents,
            result
        ]
    )

    # Replace the old history
    updated_histories = [
        updated_history
        if h.message_id == message_id
        else h
        for h in state["intent_histories"]
    ]

    return {
        "intent_histories": updated_histories
    }


def sql_generator(state: AgentState)-> dict :
    """
    generates an SQL script that solves the users query
    """

    logger.info("starting the SQL generator agent")

    latest_message = state["messages"][-1]
    current_history = next((
        h for h in state["intent_histories"] 
        if h.message_id == latest_message.id),
        None
        )
    latest_intent = current_history.intents[-1]
    
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

    result = sql_generator_llm.invoke(
        {
        "human_template":human_template
        }
    )
    pprint(result)

    return {
        "sql":result
    }


def sql_auditor(state:AgentState)->dict:
    """
    Audit the generated SQL query.
    """
    logger.info("starting the SQL auditor agent")

    latest_message = state["messages"][-1]
    current_history = next((
        h for h in state["intent_histories"] 
        if h.message_id == latest_message.id),
        None
        )
    latest_intent = current_history.intents[-1]

    human_template=f"""
    Validated user intent:
    {latest_intent.interpretation}
    SQL query :
    {state['sql'].query}

    Explanation:
    {state['sql'].explanation}

    tables_used:
    {state['sql'].tables_used}

    Columns used:
    {state["sql"].used_columns}

    """

    result = sql_auditor_llm.invoke({
        "human_template":human_template
    })

    pprint(result)
    return {
        "audit":result
    }


def result_analyst(state:AgentState)->dict:
    """
    Analyze the execution result and generate the final response.
    """

    logger.info("starting the result analyst agent")
    latest_message = state["messages"][-1]
    current_history = next((
        h for h in state["intent_histories"] 
        if h.message_id == latest_message.id),
        None
        )
    latest_intent = current_history.intents[-1]

    human_template = f"""
    Validated user intent:
    {latest_intent.interpretation}

    Execution result:
    {state["execution"]}
    """

    result = result_analyst_llm.invoke({
        "human_template":human_template
    })
    pprint(result)
    return {
        "response":result
    }


def execute(state:AgentState)->dict:
    """
    """

    logger.info("executing the SQL query")

    result = sql_executor.execute(
        state["sql"].query
    )
    pprint(result)
    return {
        "execution":ExecutionState(**result)
    }









