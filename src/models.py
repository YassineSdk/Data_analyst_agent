from pydantic import BaseModel , Field
from typing import Literal


class Message(BaseModel):
    id:str
    HumanMessages:str 
    AIMessages : str

class ConversationState(BaseModel):
    messages : list[Message]

class SQLState(BaseModel):
    query:str
    explanation:str 
    tables_used:list[str]
    used_columns:list[str]

class AuditState(BaseModel):
    approved: bool 
    feedback: str | None = None 

class ExecutionState(BaseModel):
    success: bool
    columns: list[str] | None = None
    result: list[list] | None = None
    error: str | None = None 

class Response(BaseModel):
    answer: str 
    export_file:str | None = None 
    visualization: bool = Field(
        default=False,
        description="""
        Whether the execution result contains enough meaningful structure 
        to support a useful visualization. Return true when the result 
        contains a meaningful dimension, category, time series, or multiple 
        comparable metrics. Return false for a single aggregated value such 
        as total sales or total revenue with no dimension. Base this decision
        only on the execution result."
        """
    )

class IntentState(BaseModel):
    interpretation: str 
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="""
        ranges from 0 to 1 and mesures the level 
        of clarity and information the the agent has 
        over the user query 
            """)
    feedback : str | None = None
    needs_clarification: bool = False
    clarification: str | None = Field(
        default=None,
        description="""
        The question the agent should ask the user when important
        information is missing or the request is ambiguous.
        Null when no clarification is required.
        """
        )

class IntentHistory(BaseModel):
    message_id : str 
    intents: list[IntentState] = Field(default_factory=list)

class PlotState(BaseModel):
    plottype : Literal['bar',"line","pie"]
    title : str 
    description : str | None 
    x : str 
    y : str 
    color : str | None = Field(
        description="""
        Optional column name from the execution result used to group or 
        differentiate the plotted data by color. Only use this when a 
        categorical column meaningfully adds a grouping to the chart
        otherwise return None. Never invent a column name.
        """
    ) 

class AllPlots(BaseModel):
    plots : list[PlotState]
    plot_exists : bool = False










