from typing import TypedDict, NotRequired
from models import (
        ConversationState,
        SQLState,
        AuditState,
        ExecutionState,
        Response,
        IntentHistory
    )



class AgentState(TypedDict):
    conversation: ConversationState
    data_context: str
    current_message_id:str
    intent_histories:list[IntentHistory]
    sql: NotRequired[SQLState | None ]
    audit: NotRequired[AuditState | None ]
    execution: NotRequired[ExecutionState | None ]
    response: NotRequired[Response  | None ] 
