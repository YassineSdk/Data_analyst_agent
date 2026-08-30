from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from nodes import * 
from state import AgentState
from utils import get_current_history



def intent_route(state:AgentState)->str:
    """
    it routes the graph to :
    - the sql_generater if the intent does not needs clarification
    - intent analyst if the the request needs clarification .
    by the user else the user provides feedback to it  
    """
    if state['mode'] == "Ask for clarification" :
    # current message id : 
        _,latest_intent = get_current_history(state)
    
        if latest_intent.confidence >= CONFIDENCE_THRESHOLD:
            return "sql_generator"
        else :
            return "intent_analyst"

    return "sql_generator"


def audit_route(state:AgentState)->str:
    """
    routes the graph into execute if the audit is approved 
    else it returns to the sql_generator
    """
    if state['audit'].approved:
        return "execute"

    return "sql_generator"

def plotting_route(state:AgentState)->str:
    """
    """
    if state['plots_enabled'] and 

# defining the graph 
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
    }
)


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
