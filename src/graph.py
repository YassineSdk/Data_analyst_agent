from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from nodes import * 
from state import AgentState
from utils import get_current_history
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv(".env"))



def intent_route(state:AgentState)->str:
    """
    Routes the graph after intent analysis:

    - out_of_domain: request is not analytical
    - intent_analyst: analytical request requires clarification/revision
    - sql_generator: analytical intent is ready for SQL generation  
    """
    _,latest_intent = get_current_history(state)

    # Request is outside the agent's analytical domain
    if  not latest_intent.is_analytics_query:
        return "out_of_domain"
    
    # Request is an analytical query
    if latest_intent.needs_clarification:
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
    routes the graph to either run the plotting 
    node or end the graph
    """
    if not state['plots_enabled'] :
        return  "end"

    if not state['response'].visualization :
        return  "end"

    return "plot_builder"

# defining the graph 
graph = StateGraph(AgentState)

#nodes 
graph.add_node("intent_analyst",intent_analyst)
graph.add_node("sql_generator",sql_generator)
graph.add_node("sql_auditor",sql_auditor)
graph.add_node("result_analyst",result_analyst)
graph.add_node("execute",execute)
graph.add_node("plot_builder",plot_builder)
graph.add_node("out_of_domain",out_of_domain)

#Workflow 
graph.add_edge(START,"intent_analyst")
graph.add_edge("out_of_domain",END)


graph.add_conditional_edges(
    "intent_analyst",
    intent_route,
    {
        "sql_generator": "sql_generator",
        "intent_analyst": "intent_analyst",
        "out_of_domain": "out_of_domain"
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
graph.add_conditional_edges(
    "result_analyst",
    plotting_route,
    {
        "end":END,
        "plot_builder":"plot_builder"
    }
)

graph.add_edge("plot_builder",END)

checkpointer = InMemorySaver()

Agent = graph.compile(
    checkpointer=checkpointer
)
