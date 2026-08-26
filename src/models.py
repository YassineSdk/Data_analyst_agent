from pydantic import BaseModel 


class Message(BaseModel):
    HumanMessages:str 
    AIMessages : str
    feedback : str | None = None

class ConversationState(BaseModel):
    messages : list[Messages]
    user_query: str 

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
    approved : bool = False 
    











