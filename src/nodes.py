
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
from utils import (intent_template_maker,
        read_context ,
        get_current_history
        )
from config import CONFIDENCE_THRESHOLD



Data_CONTEXT = read_context("data_context.txt")

def intent_analyst(state: AgentState) -> dict:
    
    logger.info("Starting the intent analyst")
    human_template = intent_template_maker(state)

    # Generating the new intent
    result = intent_analyst_llm.invoke(
        {
            "human_template": human_template
        }
    )

    pprint(result)
    if state['mode'] == "Ask for clarification": 
        # Derive if clarification is still needed 
        if result.confidence < CONFIDENCE_THRESHOLD:
            logger.info(
                "Confidence below threshold (%.2f). "
                "Requesting user clarification.",
                CONFIDENCE_THRESHOLD
            )

        # Pause the graph and ask the user
            feedback = interrupt(
                    {
                        "type": "intent_clarification",
                        "question": result.clarification
                    }
                )
        
            logger.info(
                    "User feedback received: %s",
                    feedback
                )

            # adding feedback to the result
            result.feedback = feedback
    
    # create new intent 
    new_history = IntentHistory(
    message_id=state["messages"][-1].id,
    intents=[result]
    )

    return {
        "intent_histories": [new_history]
    }


def sql_generator(state: AgentState)-> dict :
    """
    generates an SQL script that solves the users query
    """

    logger.info("starting the SQL generator agent")

    latest_message = state["messages"][-1]
    history,latest_intent = get_current_history(state)
    
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

    Confidence:
    {latest_intent.confidence}

    Feedback:
    {latest_intent.feedback or "None"}
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
    history,latest_intent = get_current_history(state)

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
    executes the SQL code 
    """

    logger.info("executing the SQL query")

    result = sql_executor.execute(
        state["sql"].query
    )
    pprint(result)
    return {
        "execution":ExecutionState(**result)
    }










