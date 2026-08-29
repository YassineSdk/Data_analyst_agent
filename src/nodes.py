from state import AgentState
from models import ExecutionState
from langgraph.types import interrupt

from agents import (
    sql_generator_llm,
    sql_auditor_prompt,
    result_analyst_llm,
    intent_analyst_llm
)
from excuter import sql_executor
from utils import intent_template_maker

def intent_analyst(state:AgentState)->dict:
    """
    Analyses the human query and retuns a well structured and build business query
    that the human needs to approve or add feedback so that the agent enhances it 
    """


    # making the human template
    human_template = intent_template_maker(state)

    # invoking the agent
    result = intent_analyst_llm.invoke(
        {"human_template":human_template}
    )

    # pause the graph and ask the human
    human_feedback = interrupt(
        {
            "type":"intent_approvel",
            "message_id": state["current_message_id"],
            "interpretation":state['intent'].interpretation
        }
    )

    # Process the human decision
    if human_response["approved"]:
        result.approved = True
    
    else:
        result.approved = False
        result.feedback = human_response.get("feedback")

    # storing the new intent
    history = next(
        h
        for h in state["intent_histories"]
        if h.message_id == state["current_message_id"]
    )
    history.iterations.append(result)

    return {
        "intent":state["intent_histories"]
    }


def sql_generator(state: AgentState)-> dict :
    """
    generates an SQL script that solves the users query
    """
    human_template =f"""
    User query:
    {state["conversation"].user_query}

    Data context :
    {state["data_context"]}

    feedback:
    {state['intent'].feedback}
    """

    result = sql_auditor_prompt.invoke(
        {
        "human_template":human_template
        }
    )

    return {
        "sql":result
    }


def sql_auditor(state:AgentState)->dict:
    """
    Audit the generated SQL query.
    """

    human_template=f"""
    Validated user intent:
    {state['intent'].interpretation}
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

    return {
        "audit":result
    }


def result_analyst(state:AgentState)->dict:
    """
    Analyze the execution result and generate the final response.
    """
    human_template = f"""
    Validated user intent:
    {state["intent"].interpretation}

    Execution result:
    {state["execution"]}
    """

    result = result_analyst_llm.invoke({
        "human_template":human_template
    })

    return {
        response:result
    }


def execute(state:AgentState)->dict:
    result = sql_executor.execute(
        state["sql"].query
    )

    return {
        "execution":ExecutionState(**result)
    }









