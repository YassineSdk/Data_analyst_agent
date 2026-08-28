from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from nodes import * 
from state import AgentState





def intent_route(state:AgentState)->str:
    """
    it routes the graph to the sql_generater if the intent is validated 
    by the user else the user passes feedback to it  
    """
    latest_intent = state["intents"][-1]
    if state['intent'].approved:
        return "sql_generator"

    return "intent_analyst"


def audit_route(state:AgentState)->str:
    """
    routes the graph into execute if the audit is approved 
    else it returns to the sql_generator
    """
    if state['audit'].approved:
        return "execute"

    return "sql_generator"

graph = StateGraph(AgentState)

#nodes 
graph.add_node("intent_analyst",intent_analyst)
graph.add_node("sql_generator",sql_generator)
graph.add_node("sql_auditor",sql_auditor)
graph.add_node("result_analyst",result_analyst)
graph.add_node("execute",execute)

#Workflow 

graph.add_edge(START,"intent_analyst")
graph.add_conditional_edges(
    "intent_analyst",
    intent_route,
    {
        "sql_generator": "sql_generator",
        "intent_analyst": "intent_analyst",
    })

graph.add_edge("sql_generator","sql_auditor")

graph.add_conditional_edges(
    "sql_auditor",
    audit_route,
    {
        "execute":"execute",
        "sql_generator":"sql_generator"
    }
)

graph.add_edge("execute","result_analyst")
graph.add_edge("result_analyst",END)


checkpointer = InMemorySaver()

Agent = graph.compile(
    checkpointer=checkpointer
)
