from typing import TypedDict, NotRequired
from models import (
        ConversationState,
        SQLState,
        AuditState,
        ExecutionState,
        Response,
        IntentState
    )



class AgentState(TypedDict):
    conversation: ConversationState
    data_context: str
    Intent:IntentState
    sql: NotRequired[SQLState | None ]
    audit: NotRequired[AuditState | None ]
    execution: NotRequired[ExecutionState | None ]
    response: NotRequired[Response  | None ] 
