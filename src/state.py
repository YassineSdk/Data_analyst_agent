from typing import TypedDict, NotRequired, Annotated , Literal
from models import (
        Message,
        SQLState,
        AuditState,
        ExecutionState,
        Response,
        IntentHistory
    )

from utils import add_messages,add_intent_history



class AgentState(TypedDict):
    messages: Annotated[list[Message],add_messages]
    mode : Literal["Automatic","Ask for clarification"]
    current_message_id:str
    intent_histories:Annotated[list[IntentHistory],add_intent_history]
    sql: NotRequired[SQLState | None ]
    audit: NotRequired[AuditState | None ]
    execution: NotRequired[ExecutionState | None ]
    response: NotRequired[Response  | None ] 
