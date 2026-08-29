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
    feedback : str | None = None
    approved : bool = False 

class IntentHistory(BaseModel):
    message_id : str 
    intents: list[IntentState] = Field(default_factory=list)










