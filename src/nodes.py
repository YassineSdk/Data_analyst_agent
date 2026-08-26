from state import AgentState

from agents import (
    sql_generator_llm,
    sql_auditor_prompt,
    result_analyst_llm,
    intent_analyst_llm
)




def intent_analyst(state:AgentState)->dict:
    """
    """
    human_template =f"""
    User query:
    {state["conversation"].user_query}

    Data context :
    {state["data_context"]}

    feedback:
    {state['conversation'].feedback}
    """

    result = intent_analyst_llm.invoke(
        {"human_template":human_template}
    )
    return {
        "intent":result
    }


def sql_generator(state: AgentState)-> dict :
    """
    """
    human_template =f"""
    User query:
    {state["conversation"].user_query}

    Data context :
    {state["data_context"]}

    feedback:
    {state['conversation'].feedback}
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












