from pydantic import BaseModel , Field


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
    table : list[dict] | None = None
    export_file:str | None = None 

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










